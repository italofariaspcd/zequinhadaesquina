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

# --- CSS PARA ACESSIBILIDADE E SOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.5em; }
    div[data-testid="stSidebar"] button[kind="primary"] { background-color: #ff4b4b !important; color: white !important; }
    .stTextInput>div>div>input { font-size: 1.1rem !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA IA GEMINI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.sidebar.error("⚠️ Erro de Autenticação na IA. Verifique os Secrets no Streamlit Cloud.")

def classificar_demanda(texto):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Classifique em uma palavra: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
        return model.generate_content(prompt).text.strip().upper()
    except:
        return "MERCADINHO"

def recomendar_melhor_opcao(lojas_encontradas, busca_usuario):
    hora_atual = datetime.now().hour
    resumo = ""
    for _, loja in lojas_encontradas.iterrows():
        status = "Aberta" if loja['abertura'] <= hora_atual < loja['fechamento'] else "Fechada"
        resumo += f"- {loja['name']} (Cidade: {loja['city']}, Status: {status})\n"

    prompt = f"""
    Usuário busca: "{busca_usuario}". Agora são {hora_atual}h. 
    Com base nestas opções, recomende a melhor (priorize locais abertos e acessíveis):
    {resumo}
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except:
        return "Analise as opções de locais acessíveis abaixo."

# --- BARRA LATERAL (BUSCA NACIONAL OTIMIZADA) ---
with st.sidebar:
    st.title("🌐 Zequinha Nacional")
    
    st.subheader("📍 Onde você está?")
    # Substituído Selectbox por Text Input para suportar todas as cidades do Brasil sem lentidão
    cidade_input = st.text_input("Digite sua Cidade", value="Aracaju")
    estado_input = st.text_input("UF (Sigla)", value="SE", max_chars=2).upper()
    
    st.divider()
    st.header("♿ Filtros")
    apenas_pcd = st.toggle("Apenas locais com rampa", value=True)
    
    st.divider()
    st.header("🚨 Segurança PCD")
    contato_sos = st.text_input("WhatsApp de Emergência", placeholder="79999999999")
    if st.button("🆘 ACIONAR AJUDA AGORA", type="primary"):
        if contato_sos:
            msg = f"🚨 *SOS PCD*%0AEstou em {cidade_input}/{estado_input} e preciso de auxílio imediato."
            st.markdown(f"[⚠️ CLIQUE PARA ENVIAR WHATSAPP](https://wa.me/55{contato_sos}?text={msg})")
        else:
            st.error("Informe um número de emergência.")

# --- CONTEÚDO PRINCIPAL ---
st.title("🏠 Zequinha da Esquina")
st.write(f"Conectando a comunidade PCD ao comércio em: **{cidade_input} - {estado_input}**")

col_v, col_t = st.columns([1, 6])
with col_v:
    st.write("Voz:")
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
with col_t:
    texto_input = audio['text'] if audio else ""
    busca = st.text_input("O que você procura hoje?", value=texto_input, placeholder="Ex: Farmácia com rampa")

# --- LÓGICA DE BUSCA ---
if busca:
    categoria = classificar_demanda(busca)
    st.info(f"🤖 IA identificou a categoria: **{categoria}**")
    
    try:
        conn = sqlite3.connect('zequinha.db')
        # Busca Nacional flexível usando as entradas de texto do sidebar
        query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city LIKE '%{cidade_input}%' AND state = '{estado_input}'"
        
        if apenas_pcd:
            query += " AND acessivel = 1"
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            # Recomendação Inteligente do Gemini
            recomendacao = recomendar_melhor_opcao(df, busca)
            st.subheader("💡 Sugestão do Zequinha")
            st.write(recomendacao)
            
            # Resultados
            st.map(df)
            for _, loja in df.iterrows():
                with st.expander(f"📍 {loja['name']}"):
                    st.write(f"Horário: {loja['abertura']}h às {loja['fechamento']}h")
                    st.markdown(f"[💬 Chamar no WhatsApp](https://wa.me/{loja['whatsapp']})")
        else:
            st.warning(f"Ainda não temos registros de '{categoria}' acessível em {cidade_input}. Que tal sugerir um local?")
            
    except Exception as e:
        st.error(f"Erro ao processar busca: {e}")
else:
    st.divider()
    st.write("👆 Use o microfone (ideal para quem usa muletas) ou digite para começar.")