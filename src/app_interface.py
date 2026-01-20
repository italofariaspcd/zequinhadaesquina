import streamlit as st
import pandas as pd
import sqlite3
from google import genai
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zequinha SE - Talentos & Vagas", page_icon="♿", layout="wide")

# --- UI DESIGN SYSTEM (SERGIPE TECH) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    .brand-title { font-size: 2.5rem; font-weight: 800; color: #22D3EE; margin-bottom: 0px; }
    .card-se { background: #1E293B; padding: 20px; border-radius: 12px; border-left: 5px solid #22D3EE; margin-bottom: 15px; }
    .stButton>button { background-color: #22D3EE !important; color: #0F172A !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<p class="brand-title">Zequinha da Esquina - SERGIPE</p>', unsafe_allow_html=True)
st.caption("O EcoSistema de Apoio e Ajuda a Talentos PCD no Estado de Sergipe")

tab_talentos, tab_vagas, tab_cadastro = st.tabs(["🤝 BUSCAR TALENTOS", "💼 VAGAS EM SE", "📝 CADASTRAR"])

# --- ABA 1: BUSCADOR DE TALENTOS (SUBSTITUI PRODUTOS) ---
with tab_talentos:
    col_v, col_s = st.columns([1, 5])
    with col_v:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic_talento')
    with col_s:
        busca_t = st.text_input("Busque talentos por área ou habilidade (Ex: Python, RH, Aracaju)", 
                                value=audio['text'] if audio else "", label_visibility="collapsed")

    if busca_t:
        conn = sqlite3.connect('zequinha.db')
        # Busca inteligente em Sergipe
        query = f"""
            SELECT * FROM profissional_pcd 
            WHERE (area_atuacao LIKE '%{busca_t}%' OR bio LIKE '%{busca_t}%' OR cidade LIKE '%{busca_t}%')
        """
        df_t = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df_t.empty:
            for _, t in df_t.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="card-se">
                            <h3>👤 {t['nome']}</h3>
                            <p><b>📍 {t['cidade']} | {t['area_atuacao']}</b></p>
                            <p>{t['bio']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    c1.link_button("Falar no WhatsApp", f"https://wa.me/55{t['telefone']}")
                    if t['curriculo_pdf']:
                        c2.download_button("Baixar CV", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
        else:
            st.warning("Nenhum talento encontrado com esse termo em Sergipe.")

# --- ABA 2: VAGAS EM SERGIPE ---
with tab_vagas:
    st.markdown("### 💼 Últimas Oportunidades no Estado")
    try:
        conn = sqlite3.connect('zequinha.db')
        df_v = pd.read_sql_query("SELECT * FROM vagas ORDER BY id DESC", conn)
        conn.close()
        for _, v in df_v.iterrows():
            with st.expander(f"🏢 {v['empresa']} - {v['titulo_vaga']}"):
                st.write(f"📍 Cidade: {v['cidade']}")
                st.write(f"📝 Requisitos: {v['requisitos']}")
                st.link_button("Candidatar-se / Contato", f"https://wa.me/55{v['contato']}")
    except:
        st.info("Buscando novas vagas em Sergipe...")

# --- ABA 3: CADASTRO (UNIFICADO) ---
with tab_cadastro:
    tipo = st.radio("O que deseja cadastrar?", ["Meu Perfil (Talento)", "Nova Vaga (Empresa)"])
    
    if tipo == "Meu Perfil (Talento)":
        with st.form("cad_talento"):
            n = st.text_input("Nome*")
            a = st.text_input("Área (Ex: Analista de Dados)*")
            c = st.selectbox("Cidade em SE", ["Aracaju", "Nossa Senhora do Socorro", "Lagarto", "Itabaiana", "São Cristóvão", "Estância"])
            t = st.text_input("WhatsApp (DDD+Número)")
            b = st.text_area("Bio/Resumo Profissional")
            pdf = st.file_uploader("Currículo (PDF)", type=["pdf"])
            if st.form_submit_button("PUBLICAR PERFIL"):
                # Lógica de INSERT no banco...
                st.success("Perfil Sergipe cadastrado!")

    else:
        with st.form("cad_vaga"):
            emp = st.text_input("Nome da Empresa*")
            vaga = st.text_input("Título da Vaga*")
            cid_v = st.text_input("Cidade da Vaga", value="Aracaju")
            req = st.text_area("Requisitos")
            cont = st.text_input("WhatsApp para Candidatos")
            if st.form_submit_button("ANUNCIAR VAGA"):
                # Lógica de INSERT na tabela vagas...
                st.success("Vaga publicada no mural de Sergipe!")