import streamlit as st
import pandas as pd
import sqlite3
import os

# --- GERENCIAMENTO DE INFRAESTRUTURA ---
# Define o caminho absoluto para o banco na raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'zequinha.db')

st.set_page_config(page_title="Zequinha da Esquina | Gestão Inclusiva", page_icon="♿", layout="wide")

# --- UI DESIGN SYSTEM (CYAN TECH) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp {{ background-color: #0F172A; color: #F8FAFC; font-family: 'Inter', sans-serif; }}
    .manifesto-container {{
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 40px; border-radius: 20px; border: 1px solid #334155; margin-bottom: 30px;
    }}
    .main-header {{ font-size: 2.8rem; font-weight: 800; color: #22D3EE; margin-bottom: 10px; }}
    .highlight {{ color: #22D3EE; font-weight: 600; }}
    .card-talento {{ background: #1E293B; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px; }}
    .stButton>button {{ background-color: #22D3EE !important; color: #0F172A !important; font-weight: 700 !important; border-radius: 8px !important; }}
    </style>
""", unsafe_allow_html=True)

# --- SEÇÃO 1: MANIFESTO E PROPÓSITO ---
st.markdown(f"""
    <div class="manifesto-container">
        <p class="main-header">Zequinha da Esquina</p>
        <p style="font-size: 1.1rem; color: #CBD5E1; line-height: 1.6;">
            O ecossistema definitivo de <span class="highlight">Empregabilidade PCD em Sergipe</span>. 
            Conectamos talentos de <span class="highlight">Aracaju</span> e região com oportunidades reais, 
            garantindo segurança na validação de laudos e currículos.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab_busca, tab_vagas, tab_cadastro = st.tabs(["🔍 BUSCAR TALENTOS", "💼 VAGAS", "📝 CADASTRAR"])

# --- ABA 1: BUSCA E VISUALIZAÇÃO ---
with tab_busca:
    st.markdown("### 🤝 Talentos Disponíveis em Sergipe")
    c1, c2 = st.columns([2, 1])
    with c1:
        f_def = st.multiselect("Filtrar por Deficiência:", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    with c2:
        f_cid = st.text_input("Cidade (SE)", value="Aracaju")

    if st.button("Filtrar Base de Dados"):
        try:
            conn = sqlite3.connect(DB_PATH)
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
                                <b>{t['nome']}</b> - {t['area_atuacao']}<br>
                                <small>📍 {t['cidade']} | Deficiência: {t['tipo_deficiencia']}</small>
                                <p style='color: #94A3B8; font-size: 0.9rem;'>{t['bio']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        b1, b2, b3 = st.columns(3)
                        b1.link_button("💬 WhatsApp", f"https://wa.me/55{t['telefone']}")
                        if t['curriculo_pdf']: b2.download_button(f"📄 CV {t['nome']}", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                        if t['laudo_pcd']: b3.download_button(f"🏥 Laudo {t['nome']}", data=t['laudo_pcd'], file_name=f"Laudo_{t['nome']}.pdf")
            else:
                st.info("Nenhum profissional encontrado para os filtros selecionados.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")

# --- ABA 3: CADASTRO COM PERSISTÊNCIA ---
with tab_cadastro:
    st.markdown("### 📝 Entre para o Ecossistema")
    with st.form("cadastro_se_final", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo*")
            area = st.text_input("Especialidade*")
            tipo_d = st.selectbox("Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
            tel = st.text_input("WhatsApp (DDD+Número)")
        with col2:
            cid = st.text_input("Cidade (SE)", value="Aracaju")
            link_in = st.text_input("LinkedIn")
            cv_f = st.file_uploader("Currículo (PDF)", type=["pdf"])
            laudo_f = st.file_uploader("Laudo Médico (PDF)*", type=["pdf"])

        bio = st.text_area("Resumo Profissional*")
        
        if st.form_submit_button("🚀 PUBLICAR PERFIL"):
            if nome and area and bio and laudo_f:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO profissional_pcd 
                        (nome, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (nome, cid, area, tipo_d, bio, tel, link_in, cv_f.read() if cv_f else None, laudo_f.read()))
                    conn.commit()
                    conn.close()
                    st.success("✅ Cadastro realizado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")
            else:
                st.error("Por favor, preencha os campos obrigatórios (*) e anexe o Laudo.")

# --- CENTRAL DE DADOS (VISUALIZAÇÃO ONLINE) ---
st.divider()
with st.expander("📊 PAINEL DE DADOS (ADMIN)"):
    st.write(f"Conectado ao arquivo: `{DB_PATH}`")
    if st.button("Listar Todos os Cadastros"):
        try:
            conn = sqlite3.connect(DB_PATH)
            # Carrega apenas textos para visualização rápida em tabela
            df_admin = pd.read_sql_query("SELECT id, nome, cidade, area_atuacao, tipo_deficiencia FROM profissional_pcd", conn)
            conn.close()
            if not df_admin.empty:
                st.dataframe(df_admin, use_container_width=True)
            else:
                st.warning("O banco de dados está vazio.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")