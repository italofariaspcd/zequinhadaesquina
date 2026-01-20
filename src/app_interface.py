import streamlit as st
import pandas as pd
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURAÇÃO DE INFRAESTRUTURA ---
# Caminho absoluto para garantir persistência no local correto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'zequinha.db')

st.set_page_config(page_title="Zequinha da Esquina | O Ecossistema PCD", page_icon="♿", layout="wide")

# --- FUNÇÃO DE ENVIO DE E-MAIL (BACKUP INVISÍVEL) ---
def enviar_notificacao_email(nome, area, deficiencia, tel, bio, arquivo_laudo=None):
    try:
        # Puxa credenciais das Secrets do Streamlit por segurança
        remetente = st.secrets["EMAIL_USER"]
        senha = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_DESTINATARIO"]

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = f"🆕 Novo Cadastro PCD: {nome} - {area}"

        corpo = f"""
        Olá,
        Um novo profissional acaba de se cadastrar em Sergipe:

        Nome: {nome}
        Área: {area}
        Deficiência: {deficiencia}
        WhatsApp: {tel}
        Resumo: {bio}

        O laudo médico segue em anexo para validação.
        """
        msg.attach(MIMEText(corpo, 'plain'))

        if arquivo_laudo:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(arquivo_laudo)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename=Laudo_{nome}.pdf")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# --- DESIGN SYSTEM (CYAN TECH) ---
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

# --- HOME / MANIFESTO ---
st.markdown(f"""
    <div class="manifesto-container">
        <p class="main-header">Zequinha SE</p>
        <p style="font-size: 1.1rem; color: #CBD5E1; line-height: 1.6;">
            O <span class="highlight">Ecossistema de Autonomia PCD de Sergipe</span>. 
            Nossa missão é conectar talentos de <span class="highlight">Aracaju</span> e região com o mercado de trabalho, 
            utilizando tecnologia para garantir a inclusão e a validação técnica/médica dos profissionais.
        </p>
    </div>
""", unsafe_allow_html=True)

tab_busca, tab_vagas, tab_cadastro = st.tabs(["🔍 BUSCAR TALENTOS", "💼 VAGAS", "📝 MEU PERFIL"])

# --- ABA 1: BUSCA PÚBLICA (CONSULTA SEGURA) ---
with tab_busca:
    st.markdown("### 🤝 Mural de Profissionais em SE")
    c1, c2 = st.columns([2, 1])
    with c1:
        f_def = st.multiselect("Filtrar por Deficiência:", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    with c2:
        f_cid = st.text_input("Filtrar Cidade", value="Aracaju")

    if st.button("Filtrar Base"):
        try:
            conn = sqlite3.connect(DB_PATH)
            query = "SELECT nome, cidade, area_atuacao, tipo_deficiencia, bio FROM profissional_pcd WHERE 1=1"
            if f_def: query += f" AND tipo_deficiencia IN ({str(f_def)[1:-1]})"
            if f_cid: query += f" AND cidade LIKE '%{f_cid}%'"
            
            df = pd.read_sql_query(query, conn)
            conn.close()

            if not df.empty:
                for _, t in df.iterrows():
                    with st.container():
                        st.markdown(f"""
                            <div class="card-talento">
                                <b style="font-size: 1.2rem; color: #22D3EE;">{t['nome']}</b><br>
                                <small>📍 {t['cidade']} | Deficiência: {t['tipo_deficiencia']}</small>
                                <p style='color: #CBD5E1; margin-top: 10px;'>{t['area_atuacao']}</p>
                                <p style='color: #94A3B8; font-size: 0.9rem;'>{t['bio']}</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Nenhum registro encontrado.")
        except:
            st.warning("O banco de dados está sendo inicializado.")

# --- ABA 3: CADASTRO COM ENVIO DE E-MAIL ---
with tab_cadastro:
    st.markdown("### 📝 Entre para o Ecossistema")
    with st.form("cadastro_completo_se", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo*")
            area = st.text_input("Cargo/Especialidade*")
            tipo_d = st.selectbox("Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
            tel = st.text_input("WhatsApp com DDD")
        with col2:
            cid = st.text_input("Cidade (SE)", value="Aracaju")
            link_in = st.text_input("Link LinkedIn")
            cv_f = st.file_uploader("Currículo (PDF)", type=["pdf"])
            laudo_f = st.file_uploader("Laudo PCD (PDF)*", type=["pdf"])

        bio = st.text_area("Resumo da sua trajetória profissional*")
        
        if st.form_submit_button("🚀 CADASTRAR"):
            if nome and area and bio and laudo_f:
                try:
                    laudo_blob = laudo_f.read()
                    cv_blob = cv_f.read() if cv_f else None
                    
                    # 1. Salva no Banco de Dados
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO profissional_pcd 
                        (nome, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (nome, cid, area, tipo_d, bio, tel, link_in, cv_blob, laudo_blob))
                    conn.commit()
                    conn.close()
                    
                    # 2. Envia para o E-mail (Invisível para quem está no site)
                    enviar_notificacao_email(nome, area, tipo_d, tel, bio, laudo_blob)
                    
                    st.success("✅ Perfil publicado!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro técnico: {e}")
            else:
                st.error("Por favor, preencha os campos com (*) e anexe o Laudo.")