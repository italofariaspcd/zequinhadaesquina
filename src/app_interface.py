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
    .stTextInput>div>div>input { font-size: 1.2rem; }
    .stSidebar { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA IA (GEMINI) ---
try:
    # Busca a chave nos Secrets do Streamlit
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.warning("⚠️ API Key do Gemini não detectada ou inválida. Usando motor de busca simples.")

def classificar_demanda_gemini(texto):
    """Usa IA Generativa para entender a intenção semântica do pedido"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Aja como um assistente local para o app 'Zequinha da Esquina' em Aracaju. 
        Classifique o pedido: "{texto}"
        Categorias: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE.
        Responda APENAS com o nome da categoria.
        """
        response = model.generate_content(prompt)
        return response.text.strip().upper()
    except Exception:
        # Fallback de segurança (Busca simples)
        texto = texto.lower()
        if any(p in texto for p in ["pão", "café", "bolacha"]): return "PADARIA"
        if any(p in texto for p in ["remedio", "dor", "farmacia"]): return "FARMÁCIA"
        return "MERCADINHO"

# --- BARRA LATERAL: LOCALIZAÇÃO E EMERGÊNCIA ---
st.sidebar.title("📍 Localização")
lat_user = st.sidebar.number_input("Sua Latitude", value=-10.9255, format="%.4f") # Padrão Aracaju
lon_user = st.sidebar.number_input("Sua Longitude", value=-37.0500, format="%.4f")
raio = st.sidebar.slider("Raio de busca (km)", 0.5, 5.0, 2.0)

st.sidebar.divider()
st.sidebar.header("♿ Filtros")
apenas_pcd = st.sidebar.checkbox("Apenas locais acessíveis", value=True)

# --- NOVO: FUNCIONALIDADE DE EMERGÊNCIA (SOS PCD) ---
st.sidebar.divider()
st.sidebar.error("🚨 SEGURANÇA PCD")
contato_sos = st.sidebar.text_input("WhatsApp de Emergência", placeholder="Ex: 79999999999")

if st.sidebar.button("🆘 ACIONAR AJUDA AGORA"):
    if contato_sos:
        # Link do Maps para socorro imediato
        map_link = f"https://www.google.com/maps?q={lat_user},{lon_user}"
        mensagem_sos = (
            f"🚨 *PEDIDO DE AJUDA - ZEQUINHA DA ESQUINA* 🚨%0A%0A"
            f"Preciso de auxílio imediato. Sou um usuário PCD (Muletas).%0A"
            f"📍 Minha localização atual: {map_link}"
        )
        whatsapp_url = f"https://wa.me/55{contato_sos}?text={mensagem_sos}"
        st.sidebar.markdown(f"[⚠️ CLIQUE PARA ENVIAR WHATSAPP]({whatsapp_url})")
    else:
        st.sidebar.info("Insira um número de contato acima.")

# --- CORPO PRINCIPAL ---
st.title("🏠 Zequinha da Esquina")
st.markdown("##### Encontre o que precisa falando ou digitando.")

# Interface de Busca (Voz e Texto)
col_mic, col_txt = st.columns([1, 5])
with col_mic:
    st.write("Voz:")
    audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

with col_txt:
    transcricao = audio_data['text'] if audio_data else ""
    if transcricao: st.success(f"Entendi: {transcricao}")
    busca = st.text_input("O que você procura?", value=transcricao, placeholder="Ex: Onde tem pão quente com rampa?")

# --- RESULTADOS ---
if busca:
    categoria = classificar_demanda_gemini(busca)
    st.info(f"🤖 IA identificou: **{categoria}**")

    try:
        conn = sqlite3.connect('zequinha.db')
        query = f"SELECT name, lat, lon, acessivel, whatsapp FROM stores WHERE category = '{categoria}'"
        if apenas_pcd:
            query += " AND acessivel = 1"
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df['distancia_km'] = df.apply(lambda r: geodesic((lat_user, lon_user), (r['lat'], r['lon'])).km, axis=1)
            vizinhos = df[df['distancia_km'] <= raio].sort_values('distancia_km')

            if not vizinhos.empty:
                col_m, col_l = st.columns([2, 1])
                with col_m:
                    st.map(vizinhos)
                with col_l:
                    st.write("### Lojas próximas")
                    for _, loja in vizinhos.iterrows():
                        icon = "♿" if loja['acessivel'] == 1 else "⚠️"
                        with st.expander(f"{icon} {loja['name']}"):
                            st.write(f"Distância: {loja['distancia_km']:.2f} km")
                            st.markdown(f"[💬 Chamar no WhatsApp](https://wa.me/{loja['whatsapp']})")
            else:
                st.warning("Nenhum local encontrado neste raio.")
        else:
            st.warning("Ainda não temos lojas nesta categoria.")
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")