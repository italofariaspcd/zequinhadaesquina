import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- LÓGICA DE CLASSIFICAÇÃO À PROVA DE FALHAS ---
def classificar_demanda(texto):
    termo = texto.lower().strip()
    
    # 1. PRIORIDADE MÁXIMA: Busca Local (Funciona sem IA/API)
    # Isso garante que 'pão' nunca seja 'mercadinho'
    if any(p in termo for p in ["pão", "padaria", "massa", "café", "bolo", "biscoito"]): 
        return "PADARIA"
    if any(p in termo for p in ["remedio", "farmacia", "dor", "saude", "fralda", "vacina"]): 
        return "FARMÁCIA"
    if any(p in termo for p in ["carne", "açougue", "frango", "boi", "churrasco", "linguiça"]): 
        return "AÇOUGUE"
    if any(p in termo for p in ["tinta", "cimento", "obra", "ferramenta", "cano", "parafuso"]): 
        return "CONSTRUÇÃO"
    if any(p in termo for p in ["arroz", "feijão", "limpeza", "mercado", "leite"]):
        return "MERCADINHO"

    # 2. SEGUNDA OPÇÃO: IA Gemini (Para frases mais complexas)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Classifique em apenas UMA palavra (PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE): {texto}"
            resposta = model.generate_content(prompt).text.strip().upper()
            if resposta in ["PADARIA", "MERCADINHO", "FARMÁCIA", "CONSTRUÇÃO", "AÇOUGUE"]:
                return resposta
    except Exception:
        pass 

    # 3. ÚLTIMO CASO: Se nada acima funcionar
    return "MERCADINHO"

# --- INTERFACE LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🌐 Zequinha Nacional")
    cidade_in = st.text_input("Sua Cidade", value="Aracaju")
    estado_in = st.text_input("UF", value="SE", max_chars=2).upper()
    
    st.divider()
    st.header("♿ Acessibilidade")
    apenas_pcd = st.toggle("Apenas com rampa", value=True)
    
    st.divider()
    st.header("🚨 Segurança")
    contato_sos = st.text_input("WhatsApp SOS", placeholder="Ex: 79999999999")
    if st.button("🆘 AJUDA AGORA", type="primary"):
        if contato_sos:
            msg = f"🚨 *SOS PCD*%0AEstou em {cidade_in}/{estado_in} e preciso de auxílio imediato."
            st.markdown(f"[⚠️ ENVIAR WHATSAPP](https://wa.me/55{contato_sos}?text={msg})")

# --- CORPO DO APLICATIVO ---
st.title("🏠 Zequinha da Esquina")
st.write(f"Conectando a comunidade PCD em: **{cidade_in} - {estado_in}**")

col_v, col_t = st.columns([1, 6])
with col_v:
    st.write("Voz:")
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
with col_t:
    texto_input = audio['text'] if audio else ""
    busca = st.text_input("O que você procura?", value=texto_input, placeholder="Ex: Preciso de pão francês")

# --- PROCESSAMENTO E EXIBIÇÃO ---
if busca:
    categoria = classificar_demanda(busca)
    st.info(f"🤖 Categoria identificada: **{categoria}**")
    
    try:
        conn = sqlite3.connect('zequinha.db')
        # Busca nacional flexível
        query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city LIKE '%{cidade_in}%' AND state = '{estado_in}'"
        if apenas_pcd:
            query += " AND acessivel = 1"
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            st.success(f"Encontramos {len(df)} local(is) acessível(is)!")
            st.map(df)
            for _, loja in df.iterrows():
                with st.expander(f"📍 {loja['name']}"):
                    st.write(f"Horário: {loja['abertura']}h às {loja['fechamento']}h")
                    st.markdown(f"[💬 Chamar no WhatsApp](https://wa.me/{loja['whatsapp']})")
        else:
            st.warning(f"Ainda não temos registros de {categoria} acessível em {cidade_in}.")
    except Exception as e:
        st.error(f"Erro ao acessar banco de dados: {e}")
else:
    st.divider()
    st.write("👆 Use o microfone ou digite acima. (Ex: 'Onde tem farmácia?')")