import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(
    page_title="Zequinha da Esquina - Nacional", 
    page_icon="♿",
    layout="wide"
)

# --- CSS CUSTOMIZADO (ACESSIBILIDADE E SOS) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.5em; }
    div[data-testid="stSidebar"] button[kind="primary"] { background-color: #ff4b4b !important; color: white !important; }
    .stTextInput>div>div>input { font-size: 1.1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA IA GEMINI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.sidebar.error("⚠️ Erro de Autenticação na IA. Verifique os Secrets.")

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
        resumo += f"- {loja['name']} (Status: {status}, Acessibilidade: Sim)\n"

    prompt = f"""
    O usuário busca: "{busca_usuario}". Agora são {hora_atual}h. 
    Analise estas opções e recomende a melhor (priorize abertas e acessíveis):
    {resumo}
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except:
        return "Confira as opções abertas no mapa abaixo."

# --- BARRA LATERAL NACIONAL ---
with st.sidebar:
    st.title("🌐 Zequinha Nacional")
    
    # Busca cidades cadastradas para o filtro nacional
    try:
        conn = sqlite3.connect('zequinha.db')
        cidades_df = pd.read_sql_query("SELECT DISTINCT city, state FROM stores", conn)
        conn.close()
        opcoes = [f"{r['city']}/{r['state']}" for _, r in cidades_df.iterrows()]
    except:
        opcoes = ["Aracaju/SE"]

    local_selecionado = st.selectbox("Selecione sua Cidade", options=opcoes if opcoes else ["Aracaju/SE"])
    cidade, estado = local_selecionado.split('/')
    
    st.divider()
    st.header("♿ Filtros")
    apenas_pcd = st.toggle("Apenas locais com rampa", value=True)
    
    st.divider()
    st.header("🚨 Segurança PCD")
    contato_sos = st.text_input("WhatsApp de Emergência", placeholder="79999999999")
    if st.button("🆘 ACIONAR AJUDA AGORA", type="primary"):
        if contato_sos:
            msg = f"🚨 *SOS PCD*%0AEstou em {cidade}/{estado} e preciso de auxílio imediato."
            st.markdown(f"[⚠️ CLIQUE PARA ENVIAR WHATSAPP](https://wa.me/55{contato_sos}?text={msg})")
        else:
            st.error("Informe um número.")

# --- CONTEÚDO PRINCIPAL ---
st.title("🏠 Zequinha da Esquina")
st.write(f"Conectando você ao comércio acessível em: **{cidade} - {estado}**")

col_v, col_t = st.columns([1, 6])
with col_v:
    st.write("Voz:")
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
with col_t:
    texto_input = audio['text'] if audio else ""
    busca = st.text_input("O que você procura?", value=texto_input, placeholder="Ex: Farmácia 24h")

# --- LÓGICA DE BUSCA E RESULTADOS (RESOLVE NAMEERROR) ---
if busca:
    categoria = classificar_demanda(busca)
    st.info(f"🤖 IA identificou a categoria: **{categoria}**")
    
    try:
        conn = sqlite3.connect('zequinha.db')
        query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city = '{cidade}'"
        if apenas_pcd:
            query += " AND acessivel = 1"
        
        # A variável 'df' é definida aqui, garantindo o escopo
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            # IA de Recomendação baseada em horário e contexto
            recomendacao = recomendar_melhor_opcao(df, busca)
            st.subheader("💡 Sugestão do Zequinha")
            st.write(recomendacao)
            
            # Mapa e Listagem
            st.map(df)
            for _, loja in df.iterrows():
                with st.expander(f"📍 {loja['name']}"):
                    st.write(f"Horário: {loja['abertura']}h às {loja['fechamento']}h")
                    st.markdown(f"[💬 Chamar no WhatsApp](https://wa.me/{loja['whatsapp']})")
        else:
            st.warning(f"Nenhum local de '{categoria}' encontrado em {cidade}.")
            
    except Exception as e:
        st.error(f"Erro ao processar busca: {e}")
else:
    st.divider()
    st.write("👆 Use o microfone ou digite o que precisa para começar.")