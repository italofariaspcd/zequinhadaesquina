import streamlit as st
import pandas as pd
import sqlite3
from google import genai  # Nova biblioteca oficial
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- UI DESIGN SYSTEM (TECH DARK) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #10B981; margin-bottom: 0px; }
    .tagline { color: #94A3B8; font-size: 1.1rem; margin-top: -10px; margin-bottom: 2rem; }
    .talento-card { background: #1E293B; padding: 24px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 1.5rem; }
    .area-badge { background-color: rgba(16, 185, 129, 0.1); color: #10B981; padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; border: 1px solid rgba(16, 185, 129, 0.2); }
    .stButton>button { background-color: #10B981 !important; color: #0F172A !important; font-weight: 700 !important; border-radius: 10px !important; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE IA (NOVA API) ---
def classificar_demanda(texto):
    try:
        if "GEMINI_API_KEY" in st.secrets:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"Classifique em uma palavra: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
            )
            return response.text.strip().upper()
    except:
        pass
    return "MERCADINHO"

# --- CABEÇALHO ---
st.markdown('<p class="main-title">Zequinha da Esquina</p>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Ecossistema Tech de Autonomia para a Comunidade PCD</p>', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["🔍 Localizador", "🤝 Mural de Profissionais", "📝 Meu Perfil"])

# --- ABA 1: BUSCA ---
with tab_busca:
    with st.sidebar:
        st.markdown("### 🌐 Filtros")
        cidade_f = st.text_input("Cidade", value="Aracaju")
        estado_f = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        if st.button("🆘 ACIONAR SOS"):
            st.error("Alerta enviado!")

    col_m, col_b = st.columns([1, 6])
    with col_m:
        st.write("Voz:")
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic_search')
    with col_b:
        # CORREÇÃO: Adicionado label e label_visibility para evitar avisos de acessibilidade
        busca = st.text_input(
            label="Busca de Estabelecimentos", 
            value=audio['text'] if audio else "", 
            placeholder="O que você procura em sua região?",
            label_visibility="collapsed" 
        )

# --- ABA 2: MURAL DE TALENTOS ---
with tab_mural:
    try:
        conn = sqlite3.connect('zequinha.db')
        query = "SELECT * FROM profissional_pcd"
        df = pd.read_sql_query(query, conn)
        conn.close()
        for _, t in df.iterrows():
            st.markdown(f"""
                <div class="talento-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 1.4rem; font-weight: 700;">{t['nome']}</span>
                        <span style="color: #94A3B8;">📍 {t['cidade']} - {t['estado']}</span>
                    </div>
                    <div style="margin-top: 8px;"><span class="area-badge">{t['area_atuacao']}</span></div>
                    <p style="margin-top: 15px; color: #CBD5E1;">{t['bio']}</p>
                </div>
            """, unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            if t['telefone']: c1.link_button("WhatsApp", f"https://wa.me/55{t['telefone']}")
            if t['linkedin']: c2.link_button("LinkedIn", t['linkedin'])
            if t['curriculo_pdf']: c3.download_button("📄 PDF", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
    except:
        st.info("Inicie o banco de dados para ver os talentos.")

# --- ABA 3: CADASTRO ---
with tab_cadastro:
    with st.form("cadastro_tech", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo*")
        area = c1.text_input("Especialidade*")
        tel = c1.text_input("WhatsApp")
        
        cid = c2.text_input("Cidade", value="Aracaju")
        est = c2.text_input("UF", value="SE")
        pdf = c2.file_uploader("Currículo (PDF)", type=["pdf"])
        
        bio = st.text_area("Resumo Profissional*")
        
        if st.form_submit_button("CADASTRAR PERFIL"):
            if nome and area and bio:
                pdf_blob = pdf.read() if pdf else None
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao, telefone, curriculo_pdf) 
                    VALUES (?,?,?,?,?,?,?)
                ''', (nome, cid, est.upper(), bio, area, tel, pdf_blob))
                conn.commit()
                conn.close()
                st.success("✅ Perfil integrado!")