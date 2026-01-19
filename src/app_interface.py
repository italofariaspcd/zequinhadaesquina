import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from geopy.distance import geodesic
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA E ACESSIBILIDADE ---
st.set_page_config(
    page_title="Zequinha da Esquina - IA Acessível", 
    page_icon="♿",
    layout="wide"
)

# Estilo para alto contraste e botões grandes (UX para PCD)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #007bff; color: white; }
    .stTextInput>div>div>input { font-size: 1.3rem; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA IA (GEMINI) ---
# Segurança: A chave deve ser configurada nos 'Secrets' do Streamlit Cloud
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.warning("⚠️ API Key do Gemini não detectada. Usando motor de busca simples.")

def classificar_demanda_gemini(texto):
    """Usa IA Generativa para entender a intenção do usuário"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Você é o assistente do 'Zequinha da Esquina' em Aracaju. 
        Sua tarefa é classificar o pedido do usuário em uma dessas categorias: 
        PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE.
        Pedido: "{texto}"
        Responda APENAS com o nome da categoria em maiúsculas.
        """
        response = model.generate_content(prompt)
        return response.text.strip().upper()
    except:
        # Fallback caso a API falhe
        texto = texto.lower()
        if "pão" in texto: return "PADARIA"
        if "remedio" in texto or "dor" in texto: return "FARMÁCIA"
        return "MERCADINHO"

# --- INTERFACE LATERAL ---
st.sidebar.title("📍 Localização")
# Coordenadas padrão: 13 de Julho, Aracaju
lat_user = st.sidebar.number_input("Sua Latitude", value=-10.9255, format="%.4f")
lon_user = st.sidebar.number_input("Sua Longitude", value=-37.0500, format="%.4f")
raio = st.sidebar.slider("Raio de busca (km)", 0.5, 5.0, 2.0)

st.sidebar.divider()
st.sidebar.header("♿ Filtro PCD")
apenas_pcd = st.sidebar.checkbox("Apenas locais com rampa/acesso", value=True)

# --- CORPO DO APP ---
st.title("🏠 Zequinha da Esquina")
st.markdown("##### Encontre o que precisa falando ou digitando.")

# Busca Híbrida
col_mic, col_txt = st.columns([1, 4])

with col_mic:
    st.write("Voz:")
    audio_output = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

with col_txt:
    transcricao = audio_output['text'] if audio_output else ""
    if transcricao: st.success(f"Entendi: {transcricao}")
    busca = st.text_input("O que você procura?", value=transcricao, placeholder="Ex: Onde tem pão quentinho e rampa?")

# --- PROCESSAMENTO ---
if busca:
    categoria = classificar_demanda_gemini(busca)
    st.info(f"🤖 IA identificou: **{categoria}**")

    # Busca no banco SQLite local
    try:
        conn = sqlite3.connect('zequinha.db')
        query = f"SELECT name, lat, lon, acessivel, whatsapp FROM stores WHERE category = '{categoria}'"
        if apenas_pcd:
            query += " AND acessivel = 1"
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            # Cálculo de distância real para o usuário de Aracaju
            df['distancia_km'] = df.apply(lambda r: geodesic((lat_user, lon_user), (r['lat'], r['lon'])).km, axis=1)
            vizinhos = df[df['distancia_km'] <= raio].sort_values('distancia_km')

            if not vizinhos.empty:
                col_mapa, col_lista = st.columns([2, 1])
                with col_mapa:
                    st.map(vizinhos)
                with col_lista:
                    st.write("### Vizinhos próximos")
                    for _, loja in vizinhos.iterrows():
                        status = "♿ Acessível" if loja['acessivel'] == 1 else "⚠️ Sem rampa"
                        with st.expander(f"{loja['name']}"):
                            st.write(f"**{status}**")
                            st.write(f"Distância: {loja['distancia_km']:.2f} km")
                            st.markdown(f"[💬 Chamar no WhatsApp](https://wa.me/{loja['whatsapp']})")
            else:
                st.warning("Nenhuma loja encontrada neste raio.")
        else:
            st.warning("Ainda não temos lojas cadastradas para esta categoria.")
    except Exception as e:
        st.error(f"Erro no banco: {e}")