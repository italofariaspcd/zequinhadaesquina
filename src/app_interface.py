import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- LÓGICA DE CLASSIFICAÇÃO (ESTRUTURA DE DADOS) ---
def classificar_demanda(texto):
    termo = texto.lower().strip()
    # Mapeamento manual para garantir disponibilidade offline
    if any(p in termo for p in ["pão", "padaria", "massa", "café"]): return "PADARIA"
    if any(p in termo for p in ["remedio", "farmacia", "dor", "saude"]): return "FARMÁCIA"
    if any(p in termo for p in ["carne", "açougue", "frango"]): return "AÇOUGUE"
    if any(p in termo for p in ["tinta", "cimento", "obra"]): return "CONSTRUÇÃO"

    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Classifique em uma palavra: PADARIA, MERCADINHO, FARMÁCIA, CONSTRUÇÃO ou AÇOUGUE. Pedido: {texto}"
            response = model.generate_content(prompt)
            return response.text.strip().upper()
    except Exception:
        pass
    return "MERCADINHO"

# --- INTERFACE: CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 8])
with col_logo:
    st.write("# 🏠") # Placeholder para sua logo oficial
with col_titulo:
    st.title("Zequinha da Esquina")

# --- NAVEGAÇÃO POR ABAS ---
tab_busca, tab_mural, tab_cadastro = st.tabs(["🔍 Busca Acessível", "🤝 Mural de Talentos", "📝 Cadastrar Perfil"])

# --- ABA 1: LOCALIZADOR (ARACAJU E NACIONAL) ---
with tab_busca:
    with st.sidebar:
        st.header("📍 Localização")
        cidade_in = st.text_input("Sua Cidade", value="Aracaju")
        estado_in = st.text_input("UF", value="SE", max_chars=2).upper()
        st.divider()
        st.header("🚨 Segurança")
        contato_sos = st.text_input("WhatsApp SOS", placeholder="79999999999")
        if st.button("🆘 ACIONAR AJUDA", type="primary"):
            if contato_sos:
                msg = f"🚨 *SOS PCD*%0AEstou em {cidade_in}/{estado_in} e preciso de auxílio imediato."
                st.markdown(f"[⚠️ ENVIAR](https://wa.me/55{contato_sos}?text={msg})")

    st.write(f"Filtros ativos: **{cidade_in} - {estado_in}**")
    
    col_v, col_t = st.columns([1, 6])
    with col_v:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
    with col_t:
        texto_input = audio['text'] if audio else ""
        busca = st.text_input("O que você precisa agora?", value=texto_input)

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
                        st.markdown(f"[💬 Chamar no WhatsApp](https://wa.me/{loja['whatsapp']})")
            else:
                st.warning("Nenhum local acessível mapeado para esta categoria ainda.")
        except Exception as e:
            st.error(f"Erro de conexão com o banco de dados: {e}")

# --- ABA 2: MURAL DE TALENTOS ---
with tab_mural:
    st.header("🤝 Rede de Profissionais PCD")
    try:
        conn = sqlite3.connect('zequinha.db')
        query = """
            SELECT p.nome, p.area_atuacao, p.bio, p.cidade, p.estado, GROUP_CONCAT(c.competencia) as skills
            FROM profissional_pcd p
            LEFT JOIN competencias c ON p.id = c.profissional_id
            GROUP BY p.id
        """
        df_talentos = pd.read_sql_query(query, conn)
        conn.close()
        for _, t in df_talentos.iterrows():
            with st.container(border=True):
                st.subheader(f"{t['nome']} | {t['area_atuacao']}")
                st.caption(f"🌍 {t['cidade']} - {t['estado']}")
                st.write(f"**Bio:** {t['bio']}")
                st.write(f"**Habilidades:** `{t['skills'] if t['skills'] else 'Não informadas'}`")
    except Exception:
        st.info("O mural está sendo atualizado. Seja o primeiro a aparecer aqui!")

# --- ABA 3: CADASTRO NACIONAL ---
with tab_cadastro:
    st.header("📝 Cadastrar meu Perfil Profissional")
    with st.form("cadastro_talento", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Seu Nome Completo")
        # Campo de texto livre conforme solicitado
        area = c1.text_input("Área de Atuação", placeholder="Digite aqui sua área (ex: Engenharia de Dados)")
        
        cidade = c2.text_input("Cidade", value="Aracaju")
        estado = c2.text_input("Estado (UF)", value="SE", max_chars=2).upper()
        
        skills = st.text_input("Habilidades Técnicas (separe por vírgula)")
        bio = st.text_area("Fale sobre sua carreira e conquistas")
        
        if st.form_submit_button("Publicar no Mural Nacional"):
            if nome and area and bio:
                try:
                    conn = sqlite3.connect('zequinha.db')
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao) VALUES (?,?,?,?,?)", 
                                   (nome, cidade, estado, bio, area))
                    p_id = cursor.lastrowid
                    if skills:
                        for s in skills.split(","):
                            cursor.execute("INSERT INTO competencias (profissional_id, competencia) VALUES (?,?)", (p_id, s.strip()))
                    conn.commit()
                    conn.close()
                    st.success("Perfil cadastrado com sucesso! Já está visível na aba Mural de Talentos.")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.error("Por favor, preencha todos os campos obrigatórios (Nome, Área e Bio).")