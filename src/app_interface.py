import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina | O Ecossistema Inclusivo", page_icon="♿", layout="wide")

# --- UI DESIGN (TECH & INCLUSIVO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0F172A; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    
    /* Estilo do Manifesto */
    .manifesto-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid #334155;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .main-header { font-size: 3rem; font-weight: 800; color: #22D3EE; margin-bottom: 10px; }
    .manifesto-text { font-size: 1.15rem; color: #CBD5E1; line-height: 1.8; }
    .highlight { color: #22D3EE; font-weight: 600; }
    
    /* Cards e Tags */
    .card-talento { background: #1E293B; padding: 25px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; }
    .tag-def { background: rgba(34, 211, 238, 0.15); color: #22D3EE; padding: 4px 12px; border-radius: 50px; font-size: 0.8rem; font-weight: 600; }
    .stButton>button { background-color: #22D3EE !important; color: #0F172A !important; font-weight: 700 !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# --- SEÇÃO 1: O MANIFESTO (HOME) ---
st.markdown(f"""
    <div class="manifesto-container">
        <p class="main-header">Zequinha da Esquina</p>
        <p class="manifesto-text">
            O <span class="highlight">Zequinha da Esquina | O Ecossistema Inclusivo</span> não é apenas uma plataforma de busca; é um 
            <span class="highlight">Ecossistema de Autonomia</span>. Nosso objetivo é romper as barreiras invisíveis que 
            limitam o potencial da Pessoa com Deficiência (PCD) em nosso estado. 
            <br><br>
            <b>Como ajudamos você?</b><br>
            🚀 <span class="highlight">Empregabilidade Real:</span> Conectamos seus talentos técnicos e laudos certificados 
            diretamente ao RH de empresas comprometidas com a inclusão.<br>
            🛠️ <span class="highlight">Transparência Técnica:</span> Facilitamos a comprovação de competências e a 
            documentação médica, agilizando processos de contratação por cotas.<br>
            🤝 <span class="highlight">Rede de Apoio:</span> Criamos uma ponte entre o profissional e as 
            vagas que respeitam suas necessidades de acessibilidade.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_busca, tab_vagas, tab_cadastro = st.tabs(["🤝 BUSCAR TALENTOS", "💼 VAGAS DISPONÍVEIS", "📝 CADASTRAR MEU PERFIL"])

# --- ABA 1: BUSCADOR DE TALENTOS ---
with tab_busca:
    st.markdown("### 🔍 Central de Recrutamento Sergipe")
    c1, c2 = st.columns([2, 1])
    with c1:
        filtro_def = st.multiselect("Filtrar por Categoria de Deficiência:", 
                                   ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    with c2:
        filtro_cidade = st.text_input("Cidade em SE", placeholder="Ex: Aracaju")

    if st.button("Filtrar Base de Talentos"):
        conn = sqlite3.connect('zequinha.db')
        query = "SELECT * FROM profissional_pcd WHERE 1=1"
        if filtro_def:
            query += f" AND tipo_deficiencia IN ({str(filtro_def)[1:-1]})"
        if filtro_cidade:
            query += f" AND cidade LIKE '%{filtro_cidade}%'"
        
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            for _, t in df.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="card-talento">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="margin:0;">{t['nome']}</h3>
                                <span class="tag-def">{t['tipo_deficiencia']}</span>
                            </div>
                            <p style="color: #38BDF8; font-weight: 600; margin-top: 5px;">{t['area_atuacao']} | 📍 {t['cidade']}</p>
                            <p style="color: #94A3B8;">{t['bio']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    b1, b2, b3 = st.columns(3)
                    b1.link_button("💬 WhatsApp", f"https://wa.me/55{t['telefone']}")
                    if t['curriculo_pdf']: b2.download_button("📄 Currículo", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                    if t['laudo_pcd']: b3.download_button("🏥 Laudo Médico", data=t['laudo_pcd'], file_name=f"Laudo_{t['nome']}.pdf")
        else:
            st.warning("Nenhum profissional encontrado com estes filtros.")

# --- ABA 3: CADASTRO ---
with tab_cadastro:
    st.markdown("### 📝 Entre para o Ecossistema")
    with st.form("cadastro_se", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo*")
            area = st.text_input("Especialidade*")
            tipo_d = st.selectbox("Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
            tel = st.text_input("WhatsApp")
        with col2:
            cid = st.text_input("Cidade (SE)", value="Aracaju")
            link_in = st.text_input("LinkedIn")
            cv_f = st.file_uploader("Currículo (PDF)", type=["pdf"])
            laudo_f = st.file_uploader("Laudo PCD (PDF)*", type=["pdf"])

        bio = st.text_area("Resumo Profissional*")
        
        if st.form_submit_button("🚀 PUBLICAR NO ECOSSISTEMA"):
            if nome and area and bio and laudo_f:
                cv_blob = cv_f.read() if cv_f else None
                laudo_blob = laudo_f.read() if laudo_f else None
                
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profissional_pcd 
                    (nome, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                ''', (nome, cid, area, tipo_d, bio, tel, link_in, cv_blob, laudo_blob))
                conn.commit()
                conn.close()
                st.success("✅ Perfil integrado com sucesso!")
            else:
                st.error("Campos Nome, Área, Bio e Laudo são obrigatórios.")