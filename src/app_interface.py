import streamlit as st
import pandas as pd
import sqlite3
from google import genai
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÃO DE AMBIENTE ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- DESIGN SYSTEM: SLATE & CYAN TECH ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    
    :root {
        --bg-main: #0F172A;
        --bg-card: #1E293B;
        --accent-cyan: #22D3EE;
        --text-dim: #94A3B8;
        --text-bright: #F8FAFC;
    }

    .stApp { background-color: var(--bg-main); color: var(--text-bright); font-family: 'Inter', sans-serif; }

    /* Cards de Talentos */
    .talento-card {
        background: var(--bg-card);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .talento-card:hover { border-color: var(--accent-cyan); box-shadow: 0 0 15px rgba(34, 211, 238, 0.1); }

    /* Títulos e Tipografia */
    .hero-text { font-size: 2.8rem; font-weight: 800; color: var(--accent-cyan); margin-bottom: 0px; }
    .sub-text { color: var(--text-dim); font-size: 1.1rem; margin-top: -10px; margin-bottom: 2rem; }

    /* Botões Customizados (Estilo Botão de Ação) */
    .stButton>button {
        background: var(--accent-cyan) !important;
        color: var(--bg-main) !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Inputs e Forms */
    .stTextInput>div>div>input { background-color: #0F172A !important; color: white !important; border: 1px solid #334155 !important; }
    </style>
""", unsafe_allow_html=True)

# --- IA: CLASSIFICADOR DE DEMANDA ---
def classificar_demanda_pcd(texto):
    try:
        if "GEMINI_API_KEY" in st.secrets:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"Classifique em uma palavra (PADARIA, FARMÁCIA, MERCADO, CONSTRUÇÃO): {texto}"
            )
            return response.text.strip().upper()
    except: pass
    return "MERCADO"

# --- INTERFACE PRINCIPAL ---
st.markdown('<p class="hero-text">Zequinha da Esquina</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Ecossistema de Tecnologia, Autonomia e Inclusão Profissional</p>', unsafe_allow_html=True)

tab_local, tab_mural, tab_cadastro = st.tabs(["🔍 LOCALIZADOR ACESSÍVEL", "🤝 REDE DE TALENTOS", "📝 MEU PERFIL TECH"])

# --- ABA 1: LOCALIZADOR ---
with tab_local:
    with st.sidebar:
        st.markdown("### 🌐 Regional")
        cidade_pref = st.text_input("Cidade Base", value="Aracaju")
        estado_pref = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        if st.button("🆘 ACIONAR SOS PCD"):
            st.error("Protocolo de ajuda enviado à rede local.")

    col_v, col_t = st.columns([1, 5])
    with col_v:
        st.write("Voz:")
        audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic_input')
    with col_t:
        termo_busca = st.text_input(label="Busca", value=audio_data['text'] if audio_data else "", 
                                   placeholder="Ex: Farmácia com acesso para muletas", label_visibility="collapsed")

    if termo_busca:
        cat = classificar_demanda_pcd(termo_busca)
        st.caption(f"🤖 Inteligência sugerida: {cat}")
        # Aqui você insere seu código de st.map() vinculado ao banco stores

# --- ABA 2: MURAL DE TALENTOS (REVISADO) ---
with tab_mural:
    st.markdown("### 🤝 Profissionais e Mentores")
    try:
        conn = sqlite3.connect('zequinha.db')
        # Join para pegar skills consolidadas
        query = """
            SELECT p.*, GROUP_CONCAT(c.competencia) as skills 
            FROM profissional_pcd p 
            LEFT JOIN competencias c ON p.id = c.profissional_id 
            GROUP BY p.id ORDER BY p.id DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        for _, t in df.iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="talento-card">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-size: 1.5rem; font-weight: 700; color: #22D3EE;">{t['nome']}</span>
                            <span style="color: #64748B;">📍 {t['cidade']} - {t['estado']}</span>
                        </div>
                        <p style="color: #CBD5E1; font-weight: 600; margin-top: 5px;">{t['area_atuacao']}</p>
                        <p style="color: #94A3B8; font-size: 0.95rem;">{t['bio']}</p>
                        <div style="margin-top: 10px;">
                            <code>{t['skills'] if t['skills'] else 'Tech Stack a definir'}</code>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns(4)
                if t['telefone']: c1.link_button("💬 WhatsApp", f"https://wa.me/55{t['telefone']}")
                if t['linkedin']: c2.link_button("🔗 LinkedIn", t['linkedin'])
                if t['instagram']: c3.link_button("📸 Instagram", t['instagram'])
                if t['curriculo_pdf']: 
                    c4.download_button("📄 Currículo PDF", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                st.divider()
    except:
        st.info("O ecossistema está sendo carregado...")

# --- ABA 3: CADASTRO (FIM DA POLUIÇÃO VISUAL) ---
with tab_cadastro:
    st.markdown("### 📝 Entre para a Rede Nacional")
    with st.form("cadastro_pcd_final", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nome = st.text_input("Nome Completo*")
            area = st.text_input("Área de Atuação (Ex: Data Scientist)*")
            tel = st.text_input("Telefone (com DDD)")
            link_in = st.text_input("LinkedIn (URL)")
            
        with col_b:
            cidade = st.text_input("Cidade", value="Aracaju")
            estado = st.text_input("Estado", value="SE").upper()
            insta = st.text_input("Instagram (URL)")
            pdf_arq = st.file_uploader("Currículo Profissional (PDF)", type=["pdf"])

        bio = st.text_area("Sua trajetória profissional*")
        skills = st.text_input("Habilidades Técnicas (separe por vírgula)")
        
        if st.form_submit_button("🚀 PUBLICAR PERFIL"):
            if nome and area and bio:
                pdf_blob = pdf_arq.read() if pdf_arq else None
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao, telefone, linkedin, instagram, curriculo_pdf) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                ''', (nome, cidade, estado, bio, area, tel, link_in, insta, pdf_blob))
                
                p_id = cursor.lastrowid
                if skills:
                    for sk in skills.split(","):
                        cursor.execute("INSERT INTO competencias (profissional_id, competencia) VALUES (?,?)", (p_id, sk.strip()))
                
                conn.commit()
                conn.close()
                st.success("✅ Perfil integrado com sucesso!")
            else:
                st.error("Preencha Nome, Área e Bio.")