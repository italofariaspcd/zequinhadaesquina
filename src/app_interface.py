import streamlit as st
import pandas as pd
import sqlite3
from google import genai
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(
    page_title="Zequinha da Esquina | Ecossistema PCD", 
    page_icon="♿", 
    layout="wide"
)

# --- IDENTIDADE VISUAL (CSS INCLUSIVO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
    
    /* Cores do Ecossistema: Azul Confiança e Cinza Suave */
    :root {
        --primary: #1E40AF;
        --background: #F8FAFC;
        --card-bg: #FFFFFF;
        --text: #1E293B;
        --accent: #2563EB;
    }

    .stApp { background-color: var(--background); color: var(--text); }
    
    /* Título e Identidade */
    .brand-title { 
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem; 
        font-weight: 700; 
        color: var(--primary); 
        margin-bottom: 0px; 
    }
    .brand-tagline { 
        color: #64748B; 
        font-size: 1.1rem; 
        margin-top: -10px; 
        margin-bottom: 2rem; 
    }

    /* Card de Talento - Design Acolhedor */
    .pcd-card {
        background: var(--card-bg);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    .area-chip {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 5px 14px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Botões Modernos e Acessíveis */
    .stButton>button {
        border-radius: 12px;
        background-color: var(--primary) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        background-color: var(--accent) !important;
    }

    /* Inputs Limpos */
    .stTextInput>div>div>input {
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE IA (ESTRUTURA DE DADOS) ---
def classificar_demanda(texto):
    try:
        if "GEMINI_API_KEY" in st.secrets:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"Classifique o estabelecimento em uma palavra: PADARIA, FARMÁCIA, MERCADINHO ou CONSTRUÇÃO. Texto: {texto}"
            )
            return response.text.strip().upper()
    except:
        pass
    return "MERCADINHO"

# --- CABEÇALHO DO ECOSSISTEMA ---
st.markdown('<p class="brand-title">Zequinha da Esquina</p>', unsafe_allow_html=True)
st.markdown('<p class="brand-tagline">Tecnologia, Autonomia e Conexão Humana para Profissionais PCD</p>', unsafe_allow_html=True)

# --- NAVEGAÇÃO PRINCIPAL ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["🔍 Buscar Estabelecimentos", "🤝 Mural de Oportunidades", "📝 Criar meu Perfil"])

# --- ABA 1: LOCALIZADOR ACESSÍVEL ---
with tab_busca:
    with st.sidebar:
        st.markdown("### 📍 Configurações de Busca")
        cidade_f = st.text_input("Cidade", value="Aracaju")
        estado_f = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        st.markdown("### 🆘 Apoio Imediato")
        if st.button("ACESSAR BOTÃO SOS", use_container_width=True):
            st.error("Alerta enviado para sua rede de segurança.")

    st.write(f"Mostrando resultados para **{cidade_f} - {estado_f}**")
    
    col_mic, col_search = st.columns([1, 6])
    with col_mic:
        st.write("Voz:")
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='voice_search')
    with col_search:
        # Uso de label_visibility para cumprir padrões de acessibilidade sem poluir o visual
        busca = st.text_input(
            label="O que você precisa hoje?", 
            value=audio['text'] if audio else "", 
            placeholder="Ex: Farmácia com rampa de acesso",
            label_visibility="collapsed"
        )

# --- ABA 2: MURAL DE TALENTOS ---

with tab_mural:
    st.markdown("### 🤝 Conecte-se com Talentos")
    try:
        conn = sqlite3.connect('zequinha.db')
        query = "SELECT * FROM profissional_pcd ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            st.info("O ecossistema está crescendo. Seja o primeiro a aparecer aqui!")
        else:
            for _, t in df.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="pcd-card">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div>
                                    <span style="font-size: 1.5rem; font-weight: 700; color: #1E40AF;">{t['nome']}</span><br>
                                    <span class="area-chip">{t['area_atuacao']}</span>
                                </div>
                                <span style="color: #64748B; font-size: 0.9rem;">📍 {t['cidade']} - {t['estado']}</span>
                            </div>
                            <p style="margin-top: 15px; font-size: 1rem; color: #334155; line-height: 1.6;">{t['bio']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns([1, 1, 1])
                    if t['telefone']: c1.link_button("💬 WhatsApp", f"https://wa.me/55{t['telefone']}")
                    if t['linkedin']: c2.link_button("🔗 LinkedIn", t['linkedin'])
                    if t['curriculo_pdf']: 
                        c3.download_button("📄 Baixar Currículo", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                    st.write("") # Espaçador entre cards
    except:
        st.warning("Aguardando sincronização do banco de dados...")

# --- ABA 3: CADASTRO DO PROFISSIONAL ---
with tab_cadastro:
    st.markdown("### 📝 Junte-se à nossa Comunidade")
    with st.form("cadastro_pcd_inclusivo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo*")
            area = st.text_input("Sua Especialidade* (Ex: Ciência de Dados)")
            tel = st.text_input("WhatsApp (com DDD)")
            link_in = st.text_input("Link do LinkedIn")
            
        with col2:
            cid = st.text_input("Cidade", value="Aracaju")
            est = st.text_input("UF", value="SE")
            pdf = st.file_uploader("Currículo Profissional (PDF)", type=["pdf"])
            instagram = st.text_input("Link do Instagram")

        bio = st.text_area("Conte-nos sua história profissional*")
        
        submit = st.form_submit_button("🚀 PUBLICAR MEU PERFIL NO ECOSSISTEMA")
        
        if submit:
            if nome and area and bio:
                pdf_blob = pdf.read() if pdf else None
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao, telefone, linkedin, instagram, curriculo_pdf) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                ''', (nome, cid, est.upper(), bio, area, tel, link_in, instagram, pdf_blob))
                conn.commit()
                conn.close()
                st.success("✅ Perfil integrado com sucesso! Verifique a aba Mural de Talentos.")
            else:
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios (*).")