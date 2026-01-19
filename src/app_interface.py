import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- UI MODERNA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #f4f7f9; }
    
    .main-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 8px solid #1E3A8A;
    }
    .hero-title {
        font-size: 3rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0;
    }
    .skill-tag {
        background: #E0E7FF; color: #1E3A8A; padding: 3px 10px;
        border-radius: 15px; font-size: 0.8rem; font-weight: bold; margin-right: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_l, col_t = st.columns([1, 6])
with col_l: st.markdown("<h1 style='font-size: 5rem; margin:0;'>♿</h1>", unsafe_allow_html=True)
with col_t:
    st.markdown('<p class="hero-title">Zequinha da Esquina</p>', unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top:-15px;'>Conectando Talentos e Acessibilidade no Brasil</p>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["🔍 BUSCA ACESSÍVEL", "🤝 MURAL DE TALENTOS", "📝 CADASTRAR PERFIL"])

# --- ABA 1: BUSCA ---
with tab_busca:
    with st.sidebar:
        st.header("📍 Localização")
        cidade_f = st.text_input("Cidade", value="Aracaju")
        estado_f = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        if st.button("🆘 ACIONAR AJUDA AGORA", type="primary", use_container_width=True):
            st.warning("Protocolo de ajuda iniciado...")

    c_mic, c_input = st.columns([1, 5])
    with c_mic: 
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic_search')
    with c_input:
        busca = st.text_input("", value=audio['text'] if audio else "", placeholder="O que você precisa em sua esquina?")

# --- ABA 2: MURAL ---
with tab_mural:
    st.markdown("### 🤝 Talentos e Profissionais PCD")
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

        for _, t in df.iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="main-card">
                        <div style="display: flex; justify-content: space-between;">
                            <h2 style="margin:0; color: #1E3A8A;">👤 {t['nome']}</h2>
                            <span style="color: #64748b;">📍 {t['cidade']} - {t['estado']}</span>
                        </div>
                        <p style="font-weight: bold; color: #3B82F6; margin-top:5px;">{t['area_atuacao']}</p>
                        <p style="color: #475569;">{t['bio']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botões de Ação
                b1, b2, b3, b4 = st.columns(4)
                if t['telefone']: b1.link_button("🟢 WhatsApp", f"https://wa.me/55{t['telefone']}")
                if t['linkedin']: b2.link_button("🔵 LinkedIn", t['linkedin'])
                if t['instagram']: b3.link_button("📸 Instagram", t['instagram'])
                if t['curriculo_pdf']:
                    b4.download_button("📄 Currículo PDF", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                st.divider()
    except Exception as e:
        st.info("Mural em fase de crescimento...")

# --- ABA 3: CADASTRO ---
with tab_cadastro:
    st.markdown("### 📝 Cadastre seu Perfil Profissional")
    with st.container(border=True):
        with st.form("form_pcd_nacional", clear_on_submit=True):
            f1, f2 = st.columns(2)
            nome_c = f1.text_input("Nome Completo*")
            area_c = f1.text_input("Área de Atuação*")
            tel_c = f1.text_input("WhatsApp (com DDD)*")
            link_c = f1.text_input("URL LinkedIn")
            
            cid_c = f2.text_input("Cidade", value="Aracaju")
            est_c = f2.text_input("UF", value="SE").upper()
            inst_c = f2.text_input("URL Instagram")
            pdf_c = f2.file_uploader("Currículo em PDF", type=["pdf"])
            
            skills_c = st.text_input("Principais Habilidades (separadas por vírgula)")
            bio_c = st.text_area("Sua Trajetória Profissional")
            
            if st.form_submit_button("🚀 PUBLICAR NO MURAL NACIONAL"):
                if nome_c and area_c and bio_c:
                    pdf_blob = pdf_c.read() if pdf_c else None
                    conn = sqlite3.connect('zequinha.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO profissional_pcd (nome, cidade, estado, area_atuacao, bio, telefone, linkedin, instagram, curriculo_pdf)
                        VALUES (?,?,?,?,?,?,?,?,?)
                    ''', (nome_c, cid_c, est_c, area_c, bio_c, tel_c, link_c, inst_c, pdf_blob))
                    
                    p_id = cursor.lastrowid
                    if skills_c:
                        for sk in skills_c.split(","):
                            cursor.execute("INSERT INTO competencias (profissional_id, competencia) VALUES (?,?)", (p_id, sk.strip()))
                    
                    conn.commit()
                    conn.close()
                    st.success("✅ Perfil publicado! Agora você faz parte da rede nacional do Zequinha da Esquina.")
                else:
                    st.error("Preencha os campos obrigatórios (*)")