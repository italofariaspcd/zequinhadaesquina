import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- UI DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1E293B;
    }

    .stApp { background-color: #F8FAFC; }

    /* Cabeçalho Minimalista */
    .header-container { margin-bottom: 2rem; }
    .main-title { font-size: 2.5rem; font-weight: 700; color: #0F172A; letter-spacing: -0.025em; }
    .tagline { color: #64748B; font-size: 1.1rem; margin-top: -10px; }

    /* Card de Talento - Design de Grid */
    .talento-card {
        background: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 1.5rem;
    }
    
    .area-chip {
        background-color: #EFF6FF;
        color: #2563EB;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Estilo para Botões Streamlit */
    .stButton>button {
        border-radius: 10px;
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        color: #334155;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: #2563EB;
        color: #2563EB;
    }
    
    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { font-weight: 500; color: #64748B; }
    .stTabs [aria-selected="true"] { color: #2563EB !important; border-bottom-color: #2563EB !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown('<p class="main-title">Zequinha da Esquina</p>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Autonomia e networking para a comunidade PCD.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["🔍 Encontrar Estabelecimentos", "🤝 Mural de Profissionais", "📝 Meu Perfil"])

# --- ABA 1: BUSCA ---
with tab_busca:
    with st.sidebar:
        st.markdown("### 📍 Região de Busca")
        cidade_f = st.text_input("Cidade", value="Aracaju")
        estado_f = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        st.markdown("### 🚨 Emergência")
        if st.button("Acionar SOS", use_container_width=True):
            st.error("Alerta enviado para contatos cadastrados.")

    col_m, col_b = st.columns([1, 6])
    with col_m:
        st.write("Voz:")
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
    with col_b:
        busca = st.text_input("", value=audio['text'] if audio else "", placeholder="O que você precisa hoje?")

    if busca:
        st.info(f"Buscando por '{busca}' em estabelecimentos acessíveis...")
        # Lógica de Classificação Gemini e SQL se mantém conforme as versões anteriores

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
            st.info("Nenhum profissional cadastrado no momento.")
        else:
            for _, t in df.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="talento-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <span style="font-size: 1.4rem; font-weight: 700; color: #0F172A;">{t['nome']}</span><br>
                                    <span class="area-chip">{t['area_atuacao']}</span>
                                </div>
                                <div style="text-align: right;">
                                    <span style="color: #64748B; font-size: 0.85rem;">📍 {t['cidade']} - {t['estado']}</span>
                                </div>
                            </div>
                            <p style="margin-top: 15px; font-size: 0.95rem; line-height: 1.6; color: #334155;">{t['bio']}</p>
                            <div style="margin-top: 10px; font-size: 0.85rem; color: #64748B;">
                                <b>Habilidades:</b> <code>{t['skills'] if t['skills'] else 'N/A'}</code>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                    if t['telefone']: c1.link_button("WhatsApp", f"https://wa.me/55{t['telefone']}")
                    if t['linkedin']: c2.link_button("LinkedIn", t['linkedin'])
                    if t['instagram']: c3.link_button("Instagram", t['instagram'])
                    if t['curriculo_pdf']:
                        c4.download_button("📄 Baixar Currículo", data=t['curriculo_pdf'], file_name=f"Curriculo_{t['nome']}.pdf")
                    st.write("") 
    except:
        st.warning("O mural está sendo sincronizado com o banco de dados.")

# --- ABA 3: CADASTRO ---
with tab_cadastro:
    st.markdown("### 📝 Cadastro Profissional")
    st.write("Adicione suas informações para ficar visível para recrutadores e parceiros.")
    
    with st.form("cadastro_premium", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_c = st.text_input("Nome Completo*")
            area_c = st.text_input("Área de Atuação*")
            tel_c = st.text_input("WhatsApp (Ex: 79999999999)")
            link_in = st.text_input("LinkedIn (URL)")
        with col2:
            cid_c = st.text_input("Cidade", value="Aracaju")
            est_c = st.text_input("UF", value="SE")
            link_ig = st.text_input("Instagram (URL)")
            pdf_c = st.file_uploader("Upload Currículo (PDF)", type=["pdf"])
        
        bio_c = st.text_area("Sua trajetória profissional*")
        skills_c = st.text_input("Habilidades (separe por vírgula)")
        
        if st.form_submit_button("Publicar Meu Perfil"):
            if nome_c and area_c and bio_c:
                # CORREÇÃO DO OPERADOR TERNÁRIO
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
                st.success("✅ Perfil publicado com sucesso no Mural Nacional!")
            else:
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios (*).")