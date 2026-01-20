import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha SE | Ecossistema Inclusivo", page_icon="♿", layout="wide")

# --- UI DESIGN SYSTEM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0F172A; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    
    .manifesto-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 40px; border-radius: 20px; border: 1px solid #334155; margin-bottom: 30px;
    }
    .main-header { font-size: 3rem; font-weight: 800; color: #22D3EE; margin-bottom: 10px; }
    .highlight { color: #22D3EE; font-weight: 600; }
    
    .card-talento { background: #1E293B; padding: 25px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; }
    .tag-def { background: rgba(34, 211, 238, 0.15); color: #22D3EE; padding: 4px 12px; border-radius: 50px; font-size: 0.8rem; font-weight: 600; }
    .stButton>button { background-color: #22D3EE !important; color: #0F172A !important; font-weight: 700 !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# --- MANIFESTO (HOME) ---
st.markdown(f"""
    <div class="manifesto-container">
        <p class="main-header">Zequinha SE</p>
        <p style="font-size: 1.15rem; color: #CBD5E1; line-height: 1.8;">
            O <span class="highlight">Zequinha da Esquina - Sergipe</span> é um Ecossistema de Autonomia. 
            Nascido em <span class="highlight">Aracaju</span>, conectamos talentos PCD diretamente 
            com empresas que valorizam a diversidade técnica e a inclusão real.
            <br><br>
            🚀 <b>Empregabilidade:</b> Cadastro de currículos e laudos médicos seguros.<br>
            🛠️ <b>Conexão SE:</b> Foco total nas oportunidades e profissionais do nosso estado.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_busca, tab_vagas, tab_cadastro = st.tabs(["🤝 BUSCAR TALENTOS", "💼 VAGAS DISPONÍVEIS", "📝 CADASTRAR MEU PERFIL"])

# --- ABA 1: BUSCADOR ---
with tab_busca:
    st.markdown("### 🔍 Central de Talentos Sergipe")
    c1, c2 = st.columns([2, 1])
    with c1:
        f_def = st.multiselect("Filtrar por Deficiência:", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    with c2:
        f_cid = st.text_input("Cidade (SE)", value="Aracaju")

    if st.button("Filtrar Talentos"):
        try:
            conn = sqlite3.connect('zequinha.db')
            query = "SELECT * FROM profissional_pcd WHERE 1=1"
            if f_def: query += f" AND tipo_deficiencia IN ({str(f_def)[1:-1]})"
            if f_cid: query += f" AND cidade LIKE '%{f_cid}%'"
            df = pd.read_sql_query(query, conn)
            conn.close()

            if not df.empty:
                for _, t in df.iterrows():
                    with st.container():
                        st.markdown(f"""
                            <div class="card-talento">
                                <div style="display: flex; justify-content: space-between;">
                                    <h3 style="margin:0;">{t['nome']}</h3>
                                    <span class="tag-def">{t['tipo_deficiencia']}</span>
                                </div>
                                <p style="color: #38BDF8; font-weight: 600;">{t['area_atuacao']} | 📍 {t['cidade']}</p>
                                <p style="color: #94A3B8;">{t['bio']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        b1, b2, b3 = st.columns(3)
                        b1.link_button("💬 WhatsApp", f"https://wa.me/55{t['telefone']}")
                        if t['curriculo_pdf']: b2.download_button("📄 Currículo", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                        if t['laudo_pcd']: b3.download_button("🏥 Laudo", data=t['laudo_pcd'], file_name=f"Laudo_{t['nome']}.pdf")
            else: st.warning("Nenhum profissional encontrado.")
        except Exception as e: st.error(f"Erro ao acessar banco: {e}")

# --- ABA 3: CADASTRO (CORREÇÃO DO ERRO) ---
with tab_cadastro:
    st.markdown("### 📝 Entre para o Ecossistema")
    with st.form("cadastro_se_corrigido", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo*")
            area = st.text_input("Especialidade*")
            tipo_d = st.selectbox("Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
            tel = st.text_input("WhatsApp (Ex: 79999999999)")
        with col2:
            cid = st.text_input("Cidade (SE)", value="Aracaju")
            link_in = st.text_input("LinkedIn")
            cv_f = st.file_uploader("Currículo (PDF)", type=["pdf"])
            laudo_f = st.file_uploader("Laudo PCD (PDF)*", type=["pdf"])

        bio = st.text_area("Resumo Profissional*")
        
        if st.form_submit_button("🚀 PUBLICAR NO ECOSSISTEMA"):
            if nome and area and bio and laudo_f:
                try:
                    cv_blob = cv_f.read() if cv_f else None
                    laudo_blob = laudo_f.read() if laudo_f else None
                    
                    conn = sqlite3.connect('zequinha.db')
                    cursor = conn.cursor()
                    
                    # CORREÇÃO: 9 colunas e 9 interrogações (?), mapeando exatamente as variáveis
                    cursor.execute('''
                        INSERT INTO profissional_pcd 
                        (nome, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (nome, cid, area, tipo_d, bio, tel, link_in, cv_blob, laudo_blob))
                    
                    conn.commit()
                    conn.close()
                    st.success("✅ Perfil e Laudo integrados com sucesso em Zequinha da Esquina!")
                except Exception as e:
                    st.error(f"Erro técnico ao salvar: {e}")
            else:
                st.error("Campos Nome, Área, Bio e Laudo são obrigatórios.")