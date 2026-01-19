import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- CUSTOM CSS (ESTILIZAÇÃO) ---
st.markdown("""
    <style>
    /* Fundo e Fontes */
    .stApp { background-color: #f0f2f6; }
    .main-title { color: #1E3A8A; font-size: 3rem; font-weight: bold; margin-bottom: 0; }
    
    /* Estilo dos Cards do Mural */
    .talento-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #1E3A8A;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Botão SOS Customizado */
    div.stButton > button:first-child {
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    
    /* Estilização das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        gap: 1px;
        padding-top: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #FFFFFF; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CLASSIFICAÇÃO ---
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
            prompt = f"Classifique em uma palavra: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
            response = model.generate_content(prompt)
            return response.text.strip().upper()
    except: pass
    return "MERCADINHO"

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 7])
with col_logo:
    st.markdown("# 🏠") 
with col_titulo:
    st.markdown('<p class="main-title">Zequinha da Esquina</p>', unsafe_allow_html=True)
    st.caption("Autonomia e Oportunidades para a Comunidade PCD")

st.divider()

# --- NAVEGAÇÃO ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["🔍 BUSCA POR VOZ", "🤝 MURAL DE TALENTOS", "📝 CADASTRAR PERFIL"])

# --- ABA 1: BUSCA ---
with tab_busca:
    with st.sidebar:
        st.header("📍 Configurações")
        cidade_in = st.text_input("Cidade", value="Aracaju")
        estado_in = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        st.error("🆘 ÁREA DE EMERGÊNCIA")
        contato_sos = st.text_input("WhatsApp para SOS", placeholder="Ex: 79999999999")
        if st.button("ACIONAR SOCORRO"):
            if contato_sos:
                msg = f"🚨 *SOS PCD*%0AEstou em {cidade_in}/{estado_in} e preciso de ajuda."
                st.markdown(f"[⚠️ ENVIAR AGORA](https://wa.me/55{contato_sos}?text={msg})")

    col_mic, col_txt = st.columns([1, 5])
    with col_mic:
        st.write("Toque para falar:")
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
    with col_txt:
        texto_input = audio['text'] if audio else ""
        busca = st.text_input("O que você procura em sua esquina?", value=texto_input, placeholder="Ex: Farmácia aberta com rampa")

    if busca:
        categoria = classificar_demanda(busca)
        st.subheader(f"🎯 Resultado para: {categoria}")
        try:
            conn = sqlite3.connect('zequinha.db')
            query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city LIKE '%{cidade_in}%' AND state = '{estado_in}' AND acessivel = 1"
            df = pd.read_sql_query(query, conn)
            conn.close()
            if not df.empty:
                st.map(df)
                for _, loja in df.iterrows():
                    with st.expander(f"📍 {loja['name']}"):
                        st.write(f"🕘 {loja['abertura']}h - {loja['fechamento']}h")
                        st.markdown(f"[✅ Contato WhatsApp](https://wa.me/{loja['whatsapp']})")
            else:
                st.warning("Ainda não mapeamos locais acessíveis nesta categoria para sua região.")
        except: st.error("Erro ao carregar mapa.")

# --- ABA 2: MURAL ---
with tab_mural:
    st.header("🤝 Rede de Profissionais")
    try:
        conn = sqlite3.connect('zequinha.db')
        query = "SELECT p.*, GROUP_CONCAT(c.competencia) as skills FROM profissional_pcd p LEFT JOIN competencias c ON p.id = c.profissional_id GROUP BY p.id"
        df_talentos = pd.read_sql_query(query, conn)
        conn.close()
        
        for _, t in df_talentos.iterrows():
            st.markdown(f"""
                <div class="talento-card">
                    <h3>👤 {t['nome']}</h3>
                    <p><b>🚀 Área:</b> {t['area_atuacao']} | 📍 {t['cidade']}-{t['estado']}</p>
                    <p><b>Habilidades:</b> <code>{t['skills'] if t['skills'] else 'N/A'}</code></p>
                    <p>{t['bio']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.button("Entrar em Contato", key=f"contact_{t['id']}")
    except: st.info("Mural em fase de crescimento.")

# --- ABA 3: CADASTRO ---
with tab_cadastro:
    st.header("📝 Junte-se à Rede Nacional")
    with st.form("cadastro_novo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo")
        area = c1.text_input("Área de Atuação", placeholder="Digite sua área (Ex: Dados, IA, RH...)")
        cidade = c2.text_input("Cidade", value="Aracaju")
        estado = c2.text_input("UF", value="SE", max_chars=2).upper()
        skills = st.text_input("Suas Habilidades (separe por vírgula)")
        bio = st.text_area("Sua Trajetória Profissional")
        
        if st.form_submit_button("PUBLICAR MEU PERFIL"):
            if nome and area and bio:
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao) VALUES (?,?,?,?,?)", (nome, cidade, estado, bio, area))
                p_id = cursor.lastrowid
                if skills:
                    for s in skills.split(","):
                        cursor.execute("INSERT INTO competencias (profissional_id, competencia) VALUES (?,?)", (p_id, s.strip()))
                conn.commit()
                conn.close()
                st.success("Perfil cadastrado com sucesso!")
            else: st.error("Preencha os campos obrigatórios.")