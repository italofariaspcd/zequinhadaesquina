import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from geopy.distance import geodesic
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="Zequinha Nacional", page_icon="♿", layout="wide")

# --- CSS ACESSIBILIDADE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3em; }
    div[data-testid="stSidebar"] button[kind="primary"] { background-color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- IA GEMINI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.sidebar.error("⚠️ IA Offline")

def classificar_demanda(texto):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Categoria (uma palavra): PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
        return model.generate_content(prompt).text.strip().upper()
    except:
        return "MERCADINHO"

# --- SIDEBAR NACIONAL ---
with st.sidebar:
    st.title("🌐 Filtro Nacional")
    
    # Busca de Cidades Únicas no Banco
    conn = sqlite3.connect('zequinha.db')
    cidades_df = pd.read_sql_query("SELECT DISTINCT city, state FROM stores", conn)
    conn.close()
    
    opcoes_cidade = [f"{r['city']}/{r['state']}" for _, r in cidades_df.iterrows()]
    local_selecionado = st.selectbox("Selecione sua Cidade", options=opcoes_cidade if opcoes_cidade else ["Aracaju/SE"])
    
    cidade, estado = local_selecionado.split('/')
    
    st.divider()
    st.header("♿ Acessibilidade")
    apenas_pcd = st.toggle("Apenas locais com rampa", value=True)
    
    st.divider()
    st.header("🚨 SOS")
    contato_sos = st.text_input("WhatsApp de Emergência")
    if st.button("🆘 AJUDA AGORA", type="primary"):
        st.markdown(f"[⚠️ ENVIAR SOS](https://wa.me/55{contato_sos}?text=Preciso+de+ajuda+em+{cidade})")

# --- BUSCA ---
st.title("🏠 Zequinha da Esquina")
st.write(f"Buscando em: **{cidade} - {estado}**")

col_v, col_t = st.columns([1, 6])
with col_v:
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
with col_t:
    texto_input = audio['text'] if audio else ""
    busca = st.text_input("O que você precisa?", value=texto_input)

if busca:
    cat = classificar_demanda(busca)
    st.info(f"🤖 Categoria: {cat}")
    
    conn = sqlite3.connect('zequinha.db')
    query = f"SELECT * FROM stores WHERE category = '{cat}' AND city = '{cidade}'"
    if apenas_pcd: query += " AND acessivel = 1"
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        st.map(df)
        for _, loja in df.iterrows():
            with st.expander(f"📍 {loja['name']}"):
                st.write(f"Cidade: {loja['city']} | WhatsApp: {loja['whatsapp']}")
    else:
        st.warning("Nada encontrado nesta cidade.")

        from datetime import datetime

def recomendar_melhor_opcao(lojas_encontradas, busca_usuario):
    """Usa o Gemini para analisar a melhor opção entre os resultados"""
    hora_atual = datetime.now().hour
    
    # Criamos um resumo das lojas para a IA
    resumo_lojas = ""
    for _, loja in lojas_encontradas.iterrows():
        status = "Aberta" if loja['abertura'] <= hora_atual < loja['fechamento'] else "Fechada"
        resumo_lojas += f"- {loja['name']} (Status: {status}, Acessível: Sim)\n"

    prompt = f"""
    O usuário busca: "{busca_usuario}". 
    Agora são {hora_atual}h. 
    Com base nestas opções, qual você recomenda e por quê? 
    Seja breve e foque em acessibilidade e se está aberto.
    Opções:
    {resumo_lojas}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except:
        return "Recomendo verificar a loja mais próxima no mapa."

# No app, após carregar o DataFrame 'df':
if not df.empty:
    recomendacao = recomendar_melhor_opcao(df, busca)
    st.subheader("🤖 Sugestão do Zequinha")
    st.write(recomendacao)