import streamlit as st
import pandas as pd
import sqlite3
from geopy.distance import geodesic
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE ACESSIBILIDADE E PÁGINA ---
st.set_page_config(
    page_title="Zequinha da Esquina - Acessível", 
    page_icon="♿",
    layout="wide"
)

# Estilo customizado para alto contraste e botões grandes
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; }
    .stTextInput>div>div>input { font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO (CÉREBRO DA IA) ---
def classificar_demanda_ia(texto):
    """Simula o motor de NLP para categorizar o pedido"""
    texto = texto.lower()
    if any(p in texto for p in ["pão", "café", "sonho", "bolacha"]): return "PADARIA"
    if any(p in texto for p in ["remédio", "farmácia", "dor", "curativo"]): return "FARMÁCIA"
    if any(p in texto for p in ["lâmpada", "torneira", "prego", "parafuso", "extensão"]): return "CONSTRUÇÃO"
    if any(p in texto for p in ["carne", "churrasco", "frango", "sol"]): return "AÇOUGUE"
    return "MERCADINHO"

# --- BARRA LATERAL (GPS E FILTROS) ---
st.sidebar.header("📍 Localização e Filtros")
lat_user = st.sidebar.number_input("Sua Latitude", value=-10.9255, format="%.4f")
lon_user = st.sidebar.number_input("Sua Longitude", value=-37.0500, format="%.4f")
raio = st.sidebar.slider("Raio de busca (km)", 0.5, 5.0, 2.0)

st.sidebar.divider()
st.sidebar.header("♿ Acessibilidade")
apenas_pcd = st.sidebar.checkbox("Apenas lojas com acesso PCD", value=False)

# --- CORPO PRINCIPAL ---
st.title("🏠 Zequinha da Esquina")
st.markdown("#### O que você precisa? Fale ou digite abaixo.")

# Layout de busca híbrida (Voz + Texto)
col_mic, col_txt = st.columns([1, 5])

with col_mic:
    st.write("Voz:")
    audio_output = mic_recorder(
        start_prompt="🎤 Iniciar",
        stop_prompt="🛑 Parar",
        key='recorder'
    )

with col_txt:
    texto_transcrito = ""
    if audio_output and audio_output['text']:
        texto_transcrito = audio_output['text']
        st.success(f"Entendi: \"{texto_transcrito}\"")
    
    busca = st.text_input("Sua procura:", value=texto_transcrito, placeholder="Ex: Preciso de pão de sal quentinho")

# --- PROCESSAMENTO E RESULTADOS ---
if busca:
    categoria_identificada = classificar_demanda_ia(busca)
    st.info(f"🔍 Categoria detectada: **{categoria_identificada}**")

    try:
        # Busca no banco SQLite
        conn = sqlite3.connect('zequinha.db')
        query = f"SELECT name, category, lat, lon, acessivel, whatsapp FROM stores WHERE category = '{categoria_identificada}'"
        
        if apenas_pcd:
            query += " AND acessivel = 1"
            
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            # Cálculo de distância
            df['distancia_km'] = df.apply(lambda r: geodesic((lat_user, lon_user), (r['lat'], r['lon'])).km, axis=1)
            vizinhos = df[df['distancia_km'] <= raio].sort_values('distancia_km')

            if not vizinhos.empty:
                map_col, list_col = st.columns([2, 1])
                with map_col:
                    st.map(vizinhos)
                with list_col:
                    st.write("### Lojas próximas")
                    for _, loja in vizinhos.iterrows():
                        icon = "♿" if loja['acessivel'] == 1 else "⚠️"
                        with st.expander(f"{icon} {loja['name']}"):
                            st.write(f"**Distância:** {loja['distancia_km']:.2f} km")
                            whatsapp_link = f"https://wa.me/{loja['whatsapp']}"
                            st.markdown(f"[💬 Chamar no WhatsApp]({whatsapp_link})")
            else:
                st.warning("Nenhum vizinho encontrado neste raio.")
        else:
            st.warning(f"Ainda não temos lojas de {categoria_identificada} cadastradas.")
            
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")