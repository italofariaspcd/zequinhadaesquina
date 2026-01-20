import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina | O EcoSistema de Apoio ao PCD", page_icon="♿", layout="wide")

# --- UI DESIGN (ESTILO TECH MINIMALISTA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0F172A; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .main-header { font-size: 2.2rem; font-weight: 800; color: #22D3EE; margin-bottom: 0px; }
    .card-talento { background: #1E293B; padding: 25px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px; }
    .tag-def { background: rgba(34, 211, 238, 0.15); color: #22D3EE; padding: 4px 12px; border-radius: 50px; font-size: 0.8rem; font-weight: 600; }
    .stButton>button { background-color: #22D3EE !important; color: #0F172A !important; font-weight: 700 !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<p class="main-header">Zequinha SE: Recrutamento Inclusivo</p>', unsafe_allow_html=True)
st.caption("Conectando Talentos PCD de Sergipe com Oportunidades Reais")

tab_busca, tab_vagas, tab_cadastro = st.tabs(["🤝 BUSCAR TALENTOS", "💼 VAGAS DISPONÍVEIS", "📝 CADASTRAR PERFIL"])

# --- ABA 1: BUSCADOR DE TALENTOS (FILTRO POR DEFICIÊNCIA) ---
with tab_busca:
    st.markdown("### 🔍 Filtros de Recrutamento")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        filtro_def = st.multiselect("Filtrar por Tipo de Deficiência:", 
                                   ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    with c2:
        filtro_cidade = st.text_input("Cidade (Sergipe)", placeholder="Ex: Aracaju")

    if st.button("Pesquisar na Base de Dados"):
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
                    
                    btn_c1, btn_c2, btn_c3 = st.columns(3)
                    btn_c1.link_button("💬 WhatsApp", f"https://wa.me/55{t['telefone']}")
                    if t['curriculo_pdf']:
                        btn_c2.download_button("📄 Baixar Currículo", data=t['curriculo_pdf'], file_name=f"CV_{t['nome']}.pdf")
                    if t['laudo_pcd']:
                        btn_c3.download_button("🏥 Baixar Laudo", data=t['laudo_pcd'], file_name=f"Laudo_{t['nome']}.pdf")
                    st.divider()
        else:
            st.warning("Nenhum talento encontrado para os filtros selecionados.")

# --- ABA 3: CADASTRO COM ANEXO DE LAUDO ---
with tab_cadastro:
    st.markdown("### 📝 Criar Perfil Profissional (Sergipe)")
    with st.form("form_pcd_se", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo*")
            area = st.text_input("Cargo/Especialidade* (Ex: Analista de Sistemas)")
            tipo_d = st.selectbox("Tipo de Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
            tel = st.text_input("Telefone com DDD (Só números)")
            
        with col2:
            cid = st.text_input("Cidade (Sergipe)", value="Aracaju")
            link_in = st.text_input("URL do LinkedIn")
            # --- ÁREA DE ANEXOS ---
            cv_file = st.file_uploader("Currículo (PDF)", type=["pdf"])
            laudo_file = st.file_uploader("Laudo Médico PCD (PDF)*", type=["pdf"])

        bio = st.text_area("Breve Resumo Profissional*")
        
        if st.form_submit_button("🚀 PUBLICAR NO ECOSSISTEMA"):
            if nome and area and bio and laudo_file:
                cv_blob = cv_file.read() if cv_file else None
                laudo_blob = laudo_file.read() if laudo_file else None
                
                conn = sqlite3.connect('zequinha.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO profissional_pcd 
                    (nome, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                ''', (nome, cid, area, tipo_d, bio, tel, link_in, cv_blob, laudo_blob))
                conn.commit()
                conn.close()
                st.success("✅ Perfil e Laudo registrados! Você já está visível para empresas de Sergipe.")
            else:
                st.error("Campos obrigatórios: Nome, Área, Bio e Laudo Médico.")