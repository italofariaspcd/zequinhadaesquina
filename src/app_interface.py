import streamlit as st
import pandas as pd
import sqlite3
from google import genai  # Nova biblioteca oficial
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- LÓGICA DE CLASSIFICAÇÃO ROBUSTA (NOVA API) ---
def classificar_demanda(texto):
    termo = texto.lower().strip()
    
    # 1. Prioridade Local (Evita chamadas desnecessárias e erro 'Mercadinho')
    if any(p in termo for p in ["pão", "padaria", "massa", "café"]): return "PADARIA"
    if any(p in termo for p in ["remedio", "farmacia", "dor", "saude"]): return "FARMÁCIA"
    if any(p in termo for p in ["carne", "açougue", "frango"]): return "AÇOUGUE"
    if any(p in termo for p in ["tinta", "cimento", "obra"]): return "CONSTRUÇÃO"
    
    # 2. Tentativa via Nova API do Gemini
    try:
        if "GEMINI_API_KEY" in st.secrets:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            prompt = f"Classifique em apenas UMA palavra (PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE): {texto}"
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            resposta = response.text.strip().upper()
            if resposta in ["PADARIA", "MERCADINHO", "FARMÁCIA", "CONSTRUÇÃO", "AÇOUGUE"]:
                return resposta
    except Exception:
        pass 

    return "MERCADINHO"

# --- INTERFACE COM LOGO NO TÍTULO ---
# Criamos colunas para alinhar a logo e o título principal
col_logo, col_titulo = st.columns([1, 8])
with col_logo:
    # Use um emoji como logo ou carregue sua imagem personalizada
    st.write("# ♿") 
with col_titulo:
    st.title("Zequinha da Esquina")

# --- BARRA LATERAL NACIONAL ---
with st.sidebar:
    st.title("🌐 Configurações")
    cidade_in = st.text_input("Sua Cidade", value="Aracaju")
    estado_in = st.text_input("UF", value="SE", max_chars=2).upper()
    
    st.divider()
    st.header("🚨 Segurança")
    contato_sos = st.text_input("WhatsApp SOS", placeholder="Ex: 79999999999")
    if st.button("🆘 AJUDA AGORA", type="primary"):
        if contato_sos:
            msg = f"🚨 *SOS PCD*%0AEstou em {cidade_in}/{estado_in} e preciso de auxílio."
            st.markdown(f"[⚠️ ENVIAR](https://wa.me/55{contato_sos}?text={msg})")

# --- BUSCA E RESULTADOS ---
st.write(f"Buscando acessibilidade em: **{cidade_in} - {estado_in}**")

col_v, col_t = st.columns([1, 6])
with col_v:
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
with col_t:
    texto_input = audio['text'] if audio else ""
    busca = st.text_input("O que você procura?", value=texto_input)

if busca:
    categoria = classificar_demanda(busca)
    st.info(f"🤖 Categoria identificada: **{categoria}**")
    
    try:
        conn = sqlite3.connect('zequinha.db')
        query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city LIKE '%{cidade_in}%' AND state = '{estado_in}' AND acessivel = 1"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            st.map(df)
            for _, loja in df.iterrows():
                with st.expander(f"📍 {loja['name']}"):
                    st.write(f"Horário: {loja['abertura']}h às {loja['fechamento']}h")
                    st.markdown(f"[💬 WhatsApp](https://wa.me/{loja['whatsapp']})")
        else:
            st.warning("Nenhum local acessível encontrado para esta busca.")
    except Exception as e:
        st.error(f"Erro de conexão com os dados: {e}")