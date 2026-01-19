import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(
    page_title="Zequinha da Esquina - Brasil", 
    page_icon="♿",
    layout="wide"
)

# --- CSS PARA ACESSIBILIDADE E IMPACTO VISUAL ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.5em; }
    div[data-testid="stSidebar"] button[kind="primary"] { background-color: #ff4b4b !important; color: white !important; }
    .stTextInput>div>div>input { font-size: 1.1rem !important; border-radius: 10px; }
    .status-box { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INTELIGÊNCIA ARTIFICIAL ---
def classificar_demanda(texto):
    # 1. Tentativa via IA (Gemini)
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Classifique em apenas UMA palavra: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
        resposta = model.generate_content(prompt).text.strip().upper()
        # Validação para garantir que a IA retornou uma categoria válida
        if resposta in ["PADARIA", "MERCADINHO", "FARMÁCIA", "CONSTRUÇÃO", "AÇOUGUE"]:
            return resposta
    except Exception:
        pass # Se falhar, segue para o fallback manual

    # 2. Fallback Manual (Evita o erro de "Sempre Mercadinho")
    termo = texto.lower()
    if any(palavra in termo for palavra in ["pão", "padaria", "doce", "café", "biscoito"]): return "PADARIA"
    if any(palavra in termo for palavra in ["remedio", "farmacia", "dor", "saude", "medicação"]): return "FARMÁCIA"
    if any(palavra in termo for palavra in ["carne", "açougue", "frango", "churrasco"]): return "AÇOUGUE"
    if any(palavra in termo for palavra in ["tinta", "cimento", "obra", "construção", "ferramenta"]): return "CONSTRUÇÃO"
    return "MERCADINHO"

def recomendar_melhor_opcao(lojas_encontradas, busca_usuario):
    hora_atual = datetime.now().hour
    resumo = ""
    for _, loja in lojas_encontradas.iterrows():
        status = "Aberta" ^ (loja['abertura'] <= hora_atual < loja['fechamento'])
        status_txt = "Aberta agora" if status else "Fechada no momento"
        resumo += f"- {loja['name']} ({status_txt}, Acessível: Sim)\n"

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"O usuário busca '{busca_usuario}' às {hora_atual}h. Analise e sugira a melhor opção: {resumo}"
        return model.generate_content(prompt).text
    except:
        return "Confira as opções acessíveis listadas abaixo no mapa."

# --- INTERFACE LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🌐 Zequinha Nacional")
    
    st.subheader("📍 Sua Localização")
    cidade_input = st.text_input("Cidade", value="Aracaju")
    estado_input = st.text_input("UF", value="SE", max_chars=2).upper()
    
    st.divider()
    st.header("♿ Acessibilidade")
    apenas_pcd = st.toggle("Filtrar por rampas/acesso", value=True)
    
    st.divider()
    st.header("🚨 Segurança")
    contato_sos = st.text_input("WhatsApp SOS", placeholder="Ex: 79999999999")
    if st.button("🆘 ACIONAR AJUDA", type="primary"):
        if contato_sos:
            msg = f"🚨 *SOLICITAÇÃO DE APOIO PCD*%0AEstou em {cidade_input}/{estado_input} e preciso de assistência."
            st.markdown(f"[⚠️ ENVIAR AGORA](https://wa.me/55{contato_sos}?text={msg})")
        else:
            st.warning("Insira um número para o SOS.")

# --- CORPO DO APLICATIVO ---
st.title("🏠 Zequinha da Esquina")
st.write(f"Busca inteligente e acessível em: **{cidade_input} - {estado_input}**")

col_v, col_t = st.columns([1, 5])
with col_v:
    st.write("Voz:")
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
with col_t:
    texto_input = audio['text'] if audio else ""
    busca = st.text_input("O que você precisa?", value=texto_input, placeholder="Ex: Preciso de pão ou farmácia 24h")

# --- PROCESSAMENTO DOS RESULTADOS ---
if busca:
    categoria = classificar_demanda(busca)
    st.info(f"🤖 Categoria Identificada: **{categoria}**")
    
    try:
        conn = sqlite3.connect('zequinha.db')
        # Busca flexível por cidade e estado
        query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city LIKE '%{cidade_input}%' AND state = '{estado_input}'"
        
        if apenas_pcd:
            query += " AND acessivel = 1"
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            # IA de Recomendação
            sugestao = recomendar_melhor_opcao(df, busca)
            st.subheader("💡 Recomendação do Zequinha")
            st.write(sugestao)
            
            # Exibição Visual
            st.map(df)
            for _, loja in df.iterrows():
                with st.expander(f"📍 {loja['name']}"):
                    st.write(f"Funcionamento: {loja['abertura']}h às {loja['fechamento']}h")
                    st.markdown(f"[💬 Contato via WhatsApp](https://wa.me/{loja['whatsapp']})")
        else:
            st.warning(f"Não encontramos {categoria} com acessibilidade em {cidade_input}. Tente outra busca!")
            
    except Exception as e:
        st.error(f"Erro técnico: {e}")
else:
    st.divider()
    st.write("🌟 **Dica:** Use o comando de voz para facilitar sua navegação, Ítalo!")