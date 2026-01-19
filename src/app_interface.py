import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- LÓGICA DE INTELIGÊNCIA E CLASSIFICAÇÃO ---
def classificar_demanda(texto):
    termo = texto.lower().strip()
    # Prioridade Local (Evita erro 'Mercadinho' se a API falhar)
    if any(p in termo for p in ["pão", "padaria", "massa"]): return "PADARIA"
    if any(p in termo for p in ["remedio", "farmacia", "dor"]): return "FARMÁCIA"
    if any(p in termo for p in ["carne", "açougue", "frango"]): return "AÇOUGUE"
    if any(p in termo for p in ["tinta", "cimento", "obra"]): return "CONSTRUÇÃO"

    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Classifique em uma palavra: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
            response = model.generate_content(prompt)
            resposta = response.text.strip().upper()
            if resposta in ["PADARIA", "MERCADINHO", "FARMÁCIA", "CONSTRUÇÃO", "AÇOUGUE"]:
                return resposta
    except:
        pass
    return "MERCADINHO"

# --- INTERFACE: TÍTULO COM LOGO ---
col_l, col_t = st.columns([1, 8])
with col_l:
    st.write("# 🏠") # Substitua por st.image("logo.png") se tiver o arquivo
with col_t:
    st.title("Zequinha da Esquina")

# --- NAVEGAÇÃO POR ABAS ---
aba_busca, aba_mural, aba_cadastro = st.tabs(["🔍 Busca Acessível", "🤝 Mural de Talentos", "📝 Cadastrar Perfil"])

# --- ABA 1: BUSCA DE LOCAIS ---
with aba_busca:
    with st.sidebar:
        st.header("📍 Localização")
        cidade_in = st.text_input("Cidade", value="Aracaju")
        estado_in = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        st.header("🚨 Segurança")
        contato_sos = st.text_input("WhatsApp SOS", placeholder="Ex: 79999999999")
        if st.button("🆘 ACIONAR AJUDA", type="primary"):
            if contato_sos:
                msg = f"🚨 *SOS PCD*%0AEstou em {cidade_in}/{estado_in} e preciso de auxílio."
                st.markdown(f"[⚠️ ENVIAR WHATSAPP](https://wa.me/55{contato_sos}?text={msg})")

    st.write(f"Buscando em: **{cidade_in} - {estado_in}**")
    col_v, col_t = st.columns([1, 6])
    with col_v:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
    with col_t:
        texto_input = audio['text'] if audio else ""
        busca = st.text_input("O que você precisa hoje?", value=texto_input)

    if busca:
        categoria = classificar_demanda(busca)
        st.info(f"🤖 Categoria: **{categoria}**")
        try:
            conn = sqlite3.connect('zequinha.db')
            query = f"SELECT * FROM stores WHERE category = '{categoria}' AND city LIKE '%{cidade_in}%' AND state = '{estado_in}' AND acessivel = 1"
            df = pd.read_sql_query(query, conn)
            conn.close()
            if not df.empty:
                st.map(df)
                for _, loja in df.iterrows():
                    with st.expander(f"📍 {loja['name']}"):
                        st.write(f"Funcionamento: {loja['abertura']}h às {loja['fechamento']}h")
                        st.markdown(f"[💬 WhatsApp](https://wa.me/{loja['whatsapp']})")
            else:
                st.warning("Nenhum local acessível encontrado.")
        except Exception as e:
            st.error(f"Erro no banco: {e}")

# --- ABA 2: MURAL DE TALENTOS ---
with aba_mural:
    st.header("🤝 Profissionais PCD em Tecnologia")
    try:
        conn = sqlite3.connect('zequinha.db')
        query = """
            SELECT p.id, p.nome, p.area_atuacao, p.bio, p.cidade, p.estado, GROUP_CONCAT(c.competencia) as skills
            FROM profissional_pcd p
            LEFT JOIN competencias c ON p.id = c.profissional_id
            GROUP BY p.id
        """
        df_talentos = pd.read_sql_query(query, conn)
        conn.close()
        
        for _, t in df_talentos.iterrows():
            with st.container(border=True):
                st.subheader(f"{t['nome']} | {t['area_atuacao']}")
                st.caption(f"📍 {t['cidade']} - {t['estado']}")
                st.write(f"**Bio:** {t['bio']}")
                st.write(f"**Skills:** `{t['skills']}`")
                st.button("Ver Portfólio / Contato", key=f"btn_{t['id']}")
    except:
        st.info("O mural está sendo povoado. Seja o primeiro a se cadastrar!")

# --- ABA 3: FORMULÁRIO DE CADASTRO ---
with aba_cadastro:
    st.header("📝 Cadastro Nacional de Talentos")
    with st.form("novo_profissional", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo")
        area = c1.selectbox("Área", ["Dados & IA", "Cibersegurança", "Gestão", "Desenvolvimento"])
        cidade = c2.text_input("Cidade")
        estado = c2.text_input("UF", max_chars=2).upper()
        skills = st.text_input("Skills (separadas por vírgula)")
        bio = st.text_area("Bio Profissional")
        
        if st.form_submit_button("Publicar Perfil"):
            if nome and bio and skills:
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao) VALUES (?,?,?,?,?)", 
                               (nome, cidade, estado, bio, area))
                p_id = cursor.lastrowid
                for s in skills.split(","):
                    cursor.execute("INSERT INTO competencias (profissional_id, competencia) VALUES (?,?)", (p_id, s.strip()))
                conn.commit()
                conn.close()
                st.success("Perfil cadastrado com sucesso!")
            else:
                st.error("Preencha todos os campos.")