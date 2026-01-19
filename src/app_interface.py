import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- UI DESIGN SYSTEM (CSS TECH DARK) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Configuração Geral do Fundo */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }

    /* Títulos Estilizados */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #10B981;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }
    
    .tagline {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 2rem;
    }

    /* Cards de Profissionais (Dark Mode) */
    .talento-card {
        background: #1E293B;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 1.5rem;
        transition: border-color 0.3s ease;
    }
    .talento-card:hover {
        border-color: #10B981;
    }

    /* Badge de Área de Atuação */
    .area-badge {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10B981;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    /* Customização de Inputs e Botões */
    .stTextInput>div>div>input {
        background-color: #1E293B !important;
        color: white !important;
        border: 1px solid #334155 !important;
    }
    
    .stButton>button {
        background-color: #10B981 !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100%;
    }

    /* Sidebar Dark */
    section[data-testid="stSidebar"] {
        background-color: #1E293B;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<p class="main-title">Zequinha da Esquina</p>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Ecossistema de Autonomia e Conexão para a Comunidade PCD</p>', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["🔍 Localizador", "🤝 Mural de Profissionais", "📝 Meu Perfil"])

# --- ABA 1: BUSCA ---
with tab_busca:
    with st.sidebar:
        st.markdown("### 🌐 Filtros Regionais")
        cidade_f = st.text_input("Cidade", value="Aracaju")
        estado_f = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        st.markdown("### 🚨 Segurança")
        if st.button("🆘 ACIONAR SOS"):
            st.error("Protocolo de ajuda enviado!")

    col_m, col_b = st.columns([1, 6])
    with col_m:
        st.write("Voz:")
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
    with col_b:
        busca = st.text_input("", value=audio['text'] if audio else "", placeholder="O que você procura em sua região?")

# --- ABA 2: MURAL DE TALENTOS ---
with tab_mural:
    try:
        conn = sqlite3.connect('zequinha.db')
        query = """
            SELECT p.*, GROUP_CONCAT(c.competencia) as skills 
            FROM profissional_pcd p 
            LEFT JOIN competencias c ON p.id = c.profissional_id 
            GROUP BY p.id
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            st.info("O mural está sendo sincronizado. Aguarde os primeiros talentos!")
        else:
            for _, t in df.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="talento-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 1.4rem; font-weight: 700; color: #F8FAFC;">{t['nome']}</span>
                                <span style="color: #94A3B8; font-size: 0.85rem;">📍 {t['cidade']} - {t['estado']}</span>
                            </div>
                            <div style="margin-top: 8px;"><span class="area-badge">{t['area_atuacao']}</span></div>
                            <p style="margin-top: 15px; font-size: 0.95rem; line-height: 1.6; color: #CBD5E1;">{t['bio']}</p>
                            <div style="margin-top: 10px; font-size: 0.8rem; color: #94A3B8;">
                                <b>Tech Stack:</b> <code>{t['skills'] if t['skills'] else 'A definir'}</code>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                    if t['telefone']: c1.link_button("WhatsApp", f"https://wa.me/55{t['telefone']}")
                    if t['linkedin']: c2.link_button("LinkedIn", t['linkedin'])
                    if t['instagram']: c3.link_button("Instagram", t['instagram'])
                    if t['curriculo_pdf']:
                        c4.download_button("📄 Currículo PDF", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                    st.write("") 
    except:
        st.warning("Aguardando inicialização do banco de dados.")

# --- ABA 3: CADASTRO ---
with tab_cadastro:
    st.markdown("### 🚀 Publique seu Perfil Profissional")
    with st.form("cadastro_tech", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_c = st.text_input("Nome Completo*")
            area_c = st.text_input("Especialidade* (Ex: Segurança de Dados)")
            tel_c = st.text_input("WhatsApp")
            link_in = st.text_input("LinkedIn (Link)")
        with col2:
            cid_c = st.text_input("Cidade", value="Aracaju")
            est_c = st.text_input("UF", value="SE")
            link_ig = st.text_input("Instagram (Link)")
            pdf_c = st.file_uploader("Currículo (PDF)", type=["pdf"])
        
        bio_c = st.text_area("Resumo da sua trajetória profissional*")
        skills_c = st.text_input("Habilidades (Ex: Python, SIEM, LGPD)")
        
        if st.form_submit_button("CADASTRAR PERFIL"):
            if nome_c and area_c and bio_c:
                pdf_blob = pdf_c.read() if pdf_c else None
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profissional_pcd 
                    (nome, cidade, estado, bio, area_atuacao, telefone, linkedin, instagram, curriculo_pdf) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                ''', (nome_c, cid_c, est_c.upper(), bio_c, area_c, tel_c, link_in, link_ig, pdf_blob))
                
                p_id = cursor.lastrowid
                if skills_c:
                    for s in skills_c.split(","):
                        cursor.execute("INSERT INTO competencias (profissional_id, competencia) VALUES (?,?)", (p_id, s.strip()))
                conn.commit()
                conn.close()
                st.success("✅ Perfil integrado ao ecossistema!")