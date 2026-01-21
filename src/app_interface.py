import streamlit as st
import pandas as pd
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ======================================================
# CONFIGURAÇÃO DE INFRAESTRUTURA
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'zequinha.db')

st.set_page_config(
    page_title="Zequinha da Esquina | O Ecossistema de Apoio ao PCD",
    page_icon="♿",
    layout="wide"
)

# ======================================================
# FUNÇÃO DE ENVIO DE E-MAIL (CORRIGIDA PARA 2 ANEXOS)
# ======================================================
def enviar_notificacao_email(nome, email, area, deficiencia, tel, bio, arquivo_laudo=None, arquivo_cv=None):
    try:
        remetente = st.secrets["EMAIL_USER"]
        senha = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_DESTINATARIO"]

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = f"🆕 Novo Cadastro PCD: {nome} - {area}"

        corpo = f"""
Olá,

Um novo profissional acaba de se cadastrar no Zequinha da Esquina:

Nome: {nome}
E-mail: {email}
Área: {area}
Deficiência: {deficiencia}
WhatsApp: {tel}

Resumo profissional:
{bio}

Os documentos seguem em anexo para validação.
        """
        msg.attach(MIMEText(corpo, 'plain'))

        # Anexo 1: Laudo Médico
        if arquivo_laudo:
            part1 = MIMEBase('application', 'octet-stream')
            part1.set_payload(arquivo_laudo)
            encoders.encode_base64(part1)
            part1.add_header('Content-Disposition', f'attachment; filename=LAUDO_{nome}.pdf')
            msg.attach(part1)

        # Anexo 2: Currículo
        if arquivo_cv:
            part2 = MIMEBase('application', 'octet-stream')
            part2.set_payload(arquivo_cv)
            encoders.encode_base64(part2)
            part2.add_header('Content-Disposition', f'attachment; filename=CV_{nome}.pdf')
            msg.attach(part2)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False

# ======================================================
# DESIGN SYSTEM (CYAN TECH)
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

.stApp {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Inter', sans-serif;
}

.manifesto-container {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    padding: 40px;
    border-radius: 20px;
    border: 1px solid #334155;
    margin-bottom: 30px;
}

.main-header {
    font-size: 2.8rem;
    font-weight: 800;
    color: #22D3EE;
    margin-bottom: 10px;
}

.highlight {
    color: #22D3EE;
    font-weight: 600;
}

.card-talento {
    background: #1E293B;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #334155;
    margin-bottom: 15px;
}

.stButton > button {
    background-color: #22D3EE !important;
    color: #0F172A !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# HOME / MANIFESTO
# ======================================================
st.markdown("""
<div class="manifesto-container">
    <p class="main-header">Zequinha da Esquina</p>
    <p style="font-size:1.1rem; color:#CBD5E1; line-height:1.6;">
        O <span class="highlight">Ecossistema de Autonomia para Pessoas com Deficiência</span>.
        Nossa missão é conectar talentos de Sergipe ao mercado de trabalho,
        utilizando tecnologia para promover inclusão real, validação técnica 
        e respeito à dignidade humana.
    </p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# ABAS
# ======================================================
tab_busca, tab_vagas, tab_cadastro = st.tabs(
    ["🔍 BUSCAR TALENTOS", "💼 VAGAS", "📝 MEU PERFIL"]
)

# ======================================================
# ABA 1 — BUSCA PÚBLICA
# ======================================================
with tab_busca:
    st.markdown("### 🤝 Mural de Talentos PCD")

    c1, c2 = st.columns([2, 1])
    with c1:
        f_def = st.multiselect(
            "Filtrar por Deficiência:",
            ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"]
        )
    with c2:
        f_cid = st.text_input("Filtrar Cidade", value="Aracaju")

    if st.button("Filtrar Base"):
        try:
            conn = sqlite3.connect(DB_PATH)
            query = "SELECT nome, cidade, area_atuacao, tipo_deficiencia, bio FROM profissional_pcd WHERE 1=1"
            params = []

            if f_def:
                query += f" AND tipo_deficiencia IN ({','.join(['?']*len(f_def))})"
                params.extend(f_def)
            if f_cid:
                query += " AND cidade LIKE ?"
                params.append(f"%{f_cid}%")

            df = pd.read_sql_query(query, conn, params=params)
            conn.close()

            if not df.empty:
                for _, t in df.iterrows():
                    st.markdown(f"""
                    <div class="card-talento">
                        <b style="font-size:1.2rem; color:#22D3EE;">{t['nome']}</b><br>
                        <small>📍 {t['cidade']} | Deficiência: {t['tipo_deficiencia']}</small>
                        <p style="margin-top:10px;"><b>{t['area_atuacao']}</b></p>
                        <p style="color:#94A3B8; font-size:0.9rem;">{t['bio']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum registro encontrado.")
        except:
            st.warning("O banco de dados está sendo inicializado ou está vazio.")

# ======================================================
# ABA 3 — CADASTRO COM E-MAIL (2 ANEXOS)
# ======================================================
with tab_cadastro:
    st.markdown("### 📝 Entre para o Ecossistema")

    with st.form("cadastro_completo_se", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome Completo*")
            email = st.text_input("E-mail*")
            area = st.text_input("Cargo/Especialidade*")
            tipo_d = st.selectbox(
                "Deficiência*",
                ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"]
            )
            tel = st.text_input("WhatsApp com DDD")

        with col2:
            cid = st.text_input("Cidade (SE)", value="Aracaju")
            link_in = st.text_input("Link LinkedIn")
            cv_f = st.file_uploader("Currículo (PDF)", type=["pdf"])
            laudo_f = st.file_uploader("Laudo PCD (PDF)*", type=["pdf"])

        bio = st.text_area("Resumo da sua trajetória profissional*")

        if st.form_submit_button("🚀 CADASTRAR"):
            if nome and email and area and bio and laudo_f:
                try:
                    laudo_blob = laudo_f.read()
                    cv_blob = cv_f.read() if cv_f else None

                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    
                    # Cria a tabela se não existir (prevenção)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS profissional_pcd (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT, email TEXT, cidade TEXT, area_atuacao TEXT, 
                            tipo_deficiencia TEXT, bio TEXT, telefone TEXT, 
                            linkedin TEXT, curriculo_pdf BLOB, laudo_pcd BLOB
                        )
                    """)

                    cursor.execute("""
                        INSERT INTO profissional_pcd 
                        (nome, email, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nome, email, cid, area, tipo_d, bio, tel, link_in, cv_blob, laudo_blob))
                    
                    conn.commit()
                    conn.close()

                    # ENVIO DOS DOIS ANEXOS
                    sucesso_email = enviar_notificacao_email(
                        nome, email, area, tipo_d, tel, bio, laudo_blob, cv_blob
                    )

                    if sucesso_email:
                        st.success("✅ Perfil publicado e documentos enviados para validação!")
                    else:
                        st.warning("✅ Perfil salvo, mas houve uma falha no envio do e-mail de notificação.")
                    
                    st.balloons()

                except Exception as e:
                    st.error(f"Erro técnico ao salvar: {e}")
            else:
                st.error("Por favor, preencha todos os campos obrigatórios (*) e anexe o laudo.")