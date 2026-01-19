import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- UI MINIMALISTA (CSS CLEAN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #334155;
    }

    .stApp { background-color: #766f6f; }

    /* Títulos e Subtítulos Profissionais */
    .main-header { font-size: 2.2rem; font-weight: 600; color: #0F172A; margin-bottom: 0px; }
    .sub-header { color: #64748B; font-size: 1rem; margin-top: -10px; margin-bottom: 30px; }

    /* Cards de Talento - Design Premium */
    .card-talento {
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background-color: #F8FAFC;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .card-talento:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    /* Estilização de Botões e Inputs */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
        color: #0F172A;
        font-weight: 500;
    }
    .stTextInput>div>div>input { border-radius: 8px; }
    
    /* Destaque para a área de Atuação */
    .area-tag {
        color: #2563EB;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE CLASSIFICAÇÃO (IA) ---
def classificar_demanda(texto):
    termo = texto.lower().strip()
    if any(p in termo for p in ["pão", "padaria", "massa"]): return "PADARIA"
    if any(p in termo for p in ["remedio", "farmacia", "dor"]): return "FARMÁCIA"
    if any(p in termo for p in ["carne", "açougue", "frango"]): return "AÇOUGUE"
    if any(p in termo for p in ["tinta", "cimento", "obra"]): return "CONSTRUÇÃO"
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Classifique em uma palavra: {texto}")
            return response.text.strip().upper()
    except: pass
    return "MERCADINHO"

# --- CABEÇALHO ---
st.markdown('<p class="main-header">Zequinha da Esquina</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Conexão, Autonomia e Oportunidades PCD</p>', unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["🔍 Localizador", "🤝 Mural de Talentos", "📝 Meu Perfil"])

# --- ABA 1: BUSCA ACESSÍVEL ---
with tab_busca:
    with st.sidebar:
        st.markdown("### 📍 Região")
        cidade_f = st.text_input("Cidade", value="Aracaju")
        estado_f = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        st.markdown("### 🚨 Segurança")
        if st.button("Acionar SOS de Emergência", use_container_width=True):
            st.error("Alerta de segurança enviado.")

    col_m, col_b = st.columns([1, 6])
    with col_m:
        st.write("Voz:")
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
    with col_b:
        busca = st.text_input("", value=audio['text'] if audio else "", placeholder="O que você precisa em sua esquina?")

    if busca:
        categoria = classificar_demanda(busca)
        try:
            conn = sqlite3.connect('zequinha.db')
            query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city LIKE '%{cidade_f}%' AND state = '{estado_f}' AND acessivel = 1"
            df_lojas = pd.read_sql_query(query, conn)
            conn.close()
            if not df_lojas.empty:
                st.map(df_lojas)
                for _, loja in df_lojas.iterrows():
                    with st.expander(f"📍 {loja['name']}"):
                        st.write(f"Horário: {loja['abertura']}h às {loja['fechamento']}h")
                        st.link_button("Chamar no WhatsApp", f"https://wa.me/{loja['whatsapp']}")
            else:
                st.warning("Nenhum local acessível encontrado para esta busca.")
        except: st.error("Erro ao carregar dados do mapa.")

# --- ABA 2: MURAL DE TALENTOS ---
with tab_mural:
    try:
        conn = sqlite3.connect('zequinha.db')
        # Buscando talentos e competências
        query = """
            SELECT p.*, GROUP_CONCAT(c.competencia) as skills 
            FROM profissional_pcd p 
            LEFT JOIN competencias c ON p.id = c.profissional_id 
            GROUP BY p.id
        """
        df_talentos = pd.read_sql_query(query, conn)
        conn.close()

        if df_talentos.empty:
            st.info("O mural está sendo iniciado. Seja o primeiro a se cadastrar!")
        else:
            for _, t in df_talentos.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="card-talento">
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <span style="font-size: 1.3rem; font-weight: 600; color: #0F172A;">{t['nome']}</span>
                                <span style="color: #94A3B8; font-size: 0.85rem;">{t['cidade']} - {t['estado']}</span>
                            </div>
                            <div class="area-tag">{t['area_atuacao']}</div>
                            <p style="margin-top: 12px; font-size: 0.95rem; line-height: 1.6;">{t['bio']}</p>
                            <div style="font-size: 0.8rem; color: #64748B;">Habilidades: <code>{t['skills'] if t['skills'] else 'N/A'}</code></div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                    if t['telefone']: c1.link_button("WhatsApp", f"https://wa.me/55{t['telefone']}")
                    if t['linkedin']: c2.link_button("LinkedIn", t['linkedin'])
                    if t['instagram']: c3.link_button("Instagram", t['instagram'])
                    if t['curriculo_pdf']:
                        c4.download_button("📄 Baixar Currículo", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                    st.write("") 
    except: st.warning("Mural em manutenção.")

# --- ABA 3: CADASTRO ---
with tab_cadastro:
    st.markdown("### Cadastro de Perfil Profissional")
    with st.form("cadastro_clean", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_c = st.text_input("Nome Completo*")
            area_c = st.text_input("Área de Atuação* (Ex: Data Science)")
            tel_c = st.text_input("WhatsApp (com DDD)")
            link_in = st.text_input("Link do LinkedIn")
        with col2:
            cid_c = st.text_input("Cidade", value="Aracaju")
            est_c = st.text_input("UF", value="SE", max_chars=2).upper()
            link_ig = st.text_input("Link do Instagram")
            pdf_c = st.file_uploader("Currículo em PDF", type=["pdf"])
        
        bio_c = st.text_area("Sobre sua trajetória profissional*")
        skills_c = st.text_input("Habilidades (separe por vírgula)")
        
        if st.form_submit_button("Finalizar e Publicar Perfil"):
            if nome_c and area_c and bio_c:
                # CORREÇÃO DA SINTAXE DO PDF
                pdf_blob = pdf_c.read() if pdf_c else None
                
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profissional_pcd 
                    (nome, cidade, estado, bio, area_atuacao, telefone, linkedin, instagram, curriculo_pdf) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                ''', (nome_c, cid_c, est_c, bio_c, area_c, tel_c, link_in, link_ig, pdf_blob))
                
                p_id = cursor.lastrowid
                if skills_c:
                    for s in skills_c.split(","):
                        cursor.execute("INSERT INTO competencias (profissional_id, competencia) VALUES (?,?)", (p_id, s.strip()))
                
                conn.commit()
                conn.close()
                st.success("✅ Perfil publicado com sucesso no Mural Nacional!")
            else:
                st.error("⚠️ Por favor, preencha Nome, Área e Bio.")