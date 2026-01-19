import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- LÓGICA DE INTELIGÊNCIA (CLASSIFICAÇÃO) ---
def classificar_demanda(texto):
    # 1. Tentativa via Gemini (IA)
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Classifique em uma palavra: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
        resposta = model.generate_content(prompt).text.strip().upper()
        if resposta in ["PADARIA", "MERCADINHO", "FARMÁCIA", "CONSTRUÇÃO", "AÇOUGUE"]:
            return resposta
    except:
        pass # Se a IA falhar ou não houver chave, inicia o fallback manual

    # 2. Fallback Manual (Evita o erro de 'Sempre Mercadinho')
    t = texto.lower()
    if any(p in t for p in ["pão", "padaria", "doce", "café"]): return "PADARIA"
    if any(p in t for p in ["remedio", "farmacia", "dor", "saude"]): return "FARMÁCIA"
    if any(p in t for p in ["carne", "açougue", "frango"]): return "AÇOUGUE"
    if any(p in t for p in ["tinta", "cimento", "obra"]): return "CONSTRUÇÃO"
    return "MERCADINHO"

# --- SIDEBAR NACIONAL ---
with st.sidebar:
    st.title("🌐 Zequinha Nacional")
    cidade_in = st.text_input("Sua Cidade", value="Aracaju")
    estado_in = st.text_input("UF", value="SE", max_chars=2).upper()
    
    st.divider()
    st.header("♿ Filtros")
    apenas_pcd = st.toggle("Apenas locais com rampa", value=True)
    
    st.divider()
    st.header("🚨 Segurança")
    contato_sos = st.text_input("WhatsApp SOS", placeholder="Ex: 79999999999")
    if st.button("🆘 AJUDA AGORA", type="primary"):
        if contato_sos:
            msg = f"🚨 *SOS PCD*%0AEstou em {cidade_in}/{estado_in} e preciso de auxílio."
            st.markdown(f"[⚠️ ENVIAR WHATSAPP](https://wa.me/55{contato_sos}?text={msg})")

# --- INTERFACE PRINCIPAL ---
st.title("🏠 Zequinha da Esquina")
st.write(f"Buscando acessibilidade em: **{cidade_in} - {estado_in}**")

col_v, col_t = st.columns([1, 6])
with col_v:
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
with col_t:
    texto_input = audio['text'] if audio else ""
    busca = st.text_input("O que você procura?", value=texto_input)

if busca:
    categoria = classificar_demanda(busca)
    st.info(f"🤖 Categoria: **{categoria}**")
    
    try:
        conn = sqlite3.connect('zequinha.db')
        query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city LIKE '%{cidade_in}%' AND state = '{estado_in}'"
        if apenas_pcd: query += " AND acessivel = 1"
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            st.map(df)
            for _, loja in df.iterrows():
                with st.expander(f"📍 {loja['name']}"):
                    st.write(f"Horário: {loja['abertura']}h às {loja['fechamento']}h")
                    st.markdown(f"[💬 WhatsApp](https://wa.me/{loja['whatsapp']})")
        else:
            st.warning("Nada encontrado com esses filtros.")
    except Exception as e:
        st.error(f"Erro no banco de dados: {e}")