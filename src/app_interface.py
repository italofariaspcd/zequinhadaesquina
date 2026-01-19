import streamlit as st
import pandas as pd
import sqlite3
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

    .stApp { background-color: #FFFFFF; }

    /* Título e Subtítulos */
    .main-header { font-size: 2.2rem; font-weight: 600; color: #0F172A; margin-bottom: 0px; }
    .sub-header { color: #64748B; font-size: 1rem; margin-top: -10px; margin-bottom: 30px; }

    /* Cards de Talento - Minimalismo Puro */
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

    /* Botões Customizados */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
        color: #0F172A;
        font-weight: 500;
        transition: 0.2s;
    }
    .stButton>button:hover {
        border-color: #0F172A;
        background-color: #F8FAFC;
    }
    
    /* Input Style */
    .stTextInput>div>div>input { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<p class="main-header">Zequinha da Esquina</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Conexão, Autonomia e Oportunidades PCD</p>', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["Localizador", "Mural de Talentos", "Meu Perfil"])

# --- ABA 1: BUSCA ---
with tab_busca:
    with st.sidebar:
        st.markdown("### 📍 Região")
        cidade = st.text_input("Cidade", value="Aracaju")
        estado = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        st.markdown("### 🚨 Segurança")
        if st.button("Acionar SOS de Emergência", use_container_width=True):
            st.error("Alerta enviado aos contatos de segurança.")

    col_m, col_b = st.columns([1, 6])
    with col_m:
        st.write("Voz:")
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
    with col_b:
        busca = st.text_input("", value=audio['text'] if audio else "", placeholder="O que você procura?")

# --- ABA 2: MURAL DE TALENTOS ---
with tab_mural:
    try:
        conn = sqlite3.connect('zequinha.db')
        query = "SELECT * FROM profissional_pcd"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            st.info("Nenhum perfil cadastrado no momento.")
        else:
            for _, t in df.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="card-talento">
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <span style="font-size: 1.3rem; font-weight: 600;">{t['nome']}</span>
                                <span style="color: #94A3B8; font-size: 0.85rem;">{t['cidade']} - {t['estado']}</span>
                            </div>
                            <div style="color: #3B82F6; font-weight: 500; margin-top: 4px;">{t['area_atuacao']}</div>
                            <p style="margin-top: 12px; font-size: 0.95rem; line-height: 1.6;">{t['bio']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Botões de Ação Minimalistas
                    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                    if t['telefone']: c1.link_button("WhatsApp", f"https://wa.me/55{t['telefone']}")
                    if t['linkedin']: c2.link_button("LinkedIn", t['linkedin'])
                    if t['instagram']: c3.link_button("Instagram", t['instagram'])
                    if t['curriculo_pdf']:
                        c4.download_button("Baixar Currículo (PDF)", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                    st.write("") # Espaçador
    except:
        st.warning("Inicie o banco de dados para visualizar o mural.")

# --- ABA 3: CADASTRO ---
with tab_cadastro:
    st.markdown("### Preencha seu Perfil Profissional")
    with st.form("cadastro_clean", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo")
            area = st.text_input("Área de Atuação (Ex: Data Science)")
            tel = st.text_input("WhatsApp (com DDD)")
            link_in = st.text_input("Link do LinkedIn")
        with col2:
            cid = st.text_input("Cidade", value="Aracaju")
            est = st.text_input("UF", value="SE")
            link_ig = st.text_input("Link do Instagram")
            pdf = st.file_uploader("Anexar Currículo (PDF)", type=["pdf"])
        
        bio = st.text_area("Sobre você (Bio Profissional)")
        
        if st.form_submit_button("Finalizar e Publicar Perfil"):
            if nome and area and bio:
                pdf_blob = pdf.read() if pdf: None
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao, telefone, linkedin, instagram, curriculo_pdf)
                    VALUES (?,?,?,?,?,?,?,?,?)
                ''', (nome, cid, est, bio, area, tel, link_in, link_ig, pdf_blob))
                conn.commit()
                conn.close()
                st.success("Perfil publicado com sucesso!")
            else:
                st.error("Preencha Nome, Área e Bio.")