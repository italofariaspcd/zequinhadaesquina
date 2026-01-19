import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from geopy.distance import geodesic
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(
    page_title="Zequinha da Esquina", 
    page_icon="♿",
    layout="wide"
)

# --- CSS CUSTOMIZADO PARA ACESSIBILIDADE E DESIGN ---
st.markdown("""
    <style>
    /* Estilo geral e fontes */
    .main { background-color: #0e1117; }
    
    /* Botões de Busca e Gerais */
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        height: 3em; 
        font-weight: bold;
    }
    
    /* Input de texto com melhor visibilidade */
    .stTextInput>div>div>input { 
        font-size: 1.2rem !important; 
        padding: 12px;
        border-radius: 10px;
    }

    /* Botão de SOS Específico (Vermelho) */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none;
    }
    
    /* Ajuste de espaçamento na Sidebar */
    [data-testid="stSidebar"] .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- INTEGRAÇÃO COM IA GEMINI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.sidebar.warning("⚠️ IA offline (Verifique o Secret)")

def classificar_demanda(texto):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Classifique em uma palavra: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
        response = model.generate_content(prompt)
        return response.text.strip().upper()
    except:
        return "MERCADINHO" # Fallback

# --- BARRA LATERAL (GESTÃO E SEGURANÇA) ---
with st.sidebar:
    st.title("📍 Configurações")
    
    with st.expander("📍 Sua Localização", expanded=True):
        lat_user = st.number_input("Lat", value=-10.9255, format="%.4f")
        lon_user = st.number_input("Lon", value=-37.0500, format="%.4f")
        raio = st.slider("Raio (km)", 0.5, 5.0, 2.0)
    
    st.divider()
    st.header("♿ Acessibilidade")
    apenas_pcd = st.toggle("Apenas locais com rampa", value=True)
    
    st.divider()
    st.header("🚨 Segurança PCD")
    st.caption("Envie sua localização para um contato de confiança.")
    contato_sos = st.text_input("WhatsApp (Ex: 79999999999)", key="sos_num")
    
    if st.button("🆘 ACIONAR AJUDA AGORA", type="primary"):
        if contato_sos:
            link_mapa = f"https://www.google.com/maps?q={lat_user},{lon_user}"
            msg = f"🚨 *SOS PCD - ZEQUINHA DA ESQUINA*%0APreciso de auxílio imediato em Aracaju.%0A📍 Localização: {link_mapa}"
            st.markdown(f"[⚠️ CLIQUE PARA ENVIAR WHATSAPP](https://wa.me/55{contato_sos}?text={msg})")
        else:
            st.error("Insira o número de emergência.")

# --- CONTEÚDO PRINCIPAL ---
st.title("🏠 Zequinha da Esquina")
st.write("Sua conexão inteligente com o comércio de Aracaju.")

col_v, col_t = st.columns([1, 6])
with col_v:
    st.write("Voz:")
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')

with col_t:
    texto_input = audio['text'] if audio else ""
    if texto_input:
        st.success(f"Ouvido: {texto_input}")
    busca = st.text_input("O que você precisa hoje?", value=texto_input, placeholder="Ex: Preciso de remédio para dor")

# --- LÓGICA DE BUSCA E MAPA ---
if busca:
    categoria = classificar_demanda(busca)
    st.info(f"🔍 Buscando por: **{categoria}**")

    try:
        conn = sqlite3.connect('zequinha.db')
        query = f"SELECT name, lat, lon, acessivel, whatsapp FROM stores WHERE category = '{categoria}'"
        if apenas_pcd: query += " AND acessivel = 1"
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df['distancia_km'] = df.apply(lambda r: geodesic((lat_user, lon_user), (r['lat'], r['lon'])).km, axis=1)
            vizinhos = df[df['distancia_km'] <= raio].sort_values('distancia_km')

            if not vizinhos.empty:
                m_col, l_col = st.columns([2, 1])
                with m_col:
                    st.map(vizinhos)
                with l_col:
                    st.subheader("Lojas Encontradas")
                    for _, loja in vizinhos.iterrows():
                        with st.expander(f"📍 {loja['name']}"):
                            st.write(f"Distância: {loja['distancia_km']:.2f} km")
                            st.markdown(f"[💬 WhatsApp](https://wa.me/{loja['whatsapp']})")
            else:
                st.warning("Nenhuma loja acessível neste raio.")
        else:
            st.warning("Categoria ainda não cadastrada no banco.")
    except Exception as e: