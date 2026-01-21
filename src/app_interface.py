import streamlit as st
import pandas as pd
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF

# --- CONFIGURAÇÃO DE INFRAESTRUTURA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'zequinha.db')

def init_db():
    """Inicializa o banco de dados com a estrutura profissional de BLOBs"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profissional_pcd (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT, email TEXT, cidade TEXT, area_atuacao TEXT, 
                tipo_deficiencia TEXT, bio TEXT, telefone TEXT, 
                linkedin TEXT, curriculo_pdf BLOB, laudo_pcd BLOB
            )
        """)

init_db()

st.set_page_config(page_title="Zequinha da Esquina | Sergipe", page_icon="♿", layout="wide")

# --- GERADOR DE PDF (ALGO A MAIS / AUTONOMIA) ---
def gerar_pdf_pcd(dados):
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(34, 211, 238) # Cyan Tech
    pdf.cell(200, 15, txt=fix("ZEQUINHA DA ESQUINA - CURRÍCULO PROFISSIONAL"), ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"NOME: {fix(dados['nome'].upper())}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=fix(f"E-mail: {dados['email']} | WhatsApp: {dados['tel']}"), ln=True)
    pdf.cell(200, 8, txt=fix(f"Local: {dados['cidade']} | Deficiência: {dados['tipo_d']}"), ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=fix("RESUMO PROFISSIONAL:"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=fix(dados['bio']))
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 10, txt=fix("Documento gerado pelo Ecossistema Zequinha da Esquina - Sergipe"), align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- NOTIFICAÇÃO POR E-MAIL (2 ANEXOS) ---
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

Um novo profissional acaba de se cadastrar no ecossistema Zequinha da Esquina:

Nome: {nome}
E-mail: {email}
Área: {area}
Deficiência: {deficiencia}
WhatsApp: {tel}

Resumo profissional:
{bio}

Os documentos seguem em anexo para validação técnica.
        """
        msg.attach(MIMEText(corpo, 'plain'))

        # Processamento de Anexos
        for arq_data, label in [(arquivo_laudo, "LAUDO"), (arquivo_cv, "CV")]:
            if arq_data:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(arq_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={label}_{nome}.pdf')
                msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
        return True
    except: return False

# --- DESIGN E ACESSIBILIDADE ---
st.components.v1.html("""
    <div vw class="enabled"><div vw-access-button class="active"></div><div vw-plugin-wrapper></div></div>
    <script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script>
    <script>new window.VLibras.Widget('https://vlibras.gov.br/app');</script>
""", height=0)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0F172A; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .manifesto-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 40px; border-radius: 20px; border: 1px solid #334155; margin-bottom: 30px;
    }
    .main-header { font-size: 3rem; font-weight: 800; color: #22D3EE; margin-bottom: 5px; }
    .highlight { color: #22D3EE; font-weight: 700; }
    .card-talento { background: #1E293B; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px; }
    .stButton > button { background-color: #22D3EE !important; color: #0F172A !important; font-weight: 700 !important; width: 100%; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# --- MANIFESTO ---
st.markdown(f"""
    <div class="manifesto-container">
        <p class="main-header">Zequinha da Esquina ♿</p>
        <p style="font-size: 1.2rem; color: #94A3B8; font-weight: 600;">Ecossistema de Autonomia e Inteligência de Dados PCD em Sergipe</p>
        <p style="font-size: 1.1rem; color: #CBD5E1; line-height: 1.8;">
            O <span class="highlight">Zequinha da Esquina</span> transcende a tecnologia; é um compromisso com a dignidade. 
            Utilizamos <b>Engenharia de Dados</b> para conectar o talento invisível de Sergipe às oportunidades reais. 
            Nossa plataforma garante validação técnica, segurança da informação e o 
            <b>protagonismo do profissional com deficiência</b>.
        </p>
    </div>
""", unsafe_allow_html=True)

tab_busca, tab_vagas, tab_cadastro = st.tabs(["🔍 BUSCAR TALENTOS", "💼 VAGAS", "📝 MEU PERFIL"])

# --- ABA 1: BUSCA PÚBLICA (SEGURA) ---
with tab_busca:
    st.markdown("### 🤝 Mural de Talentos PCD")
    c1, c2 = st.columns([2, 1])
    f_def = c1.multiselect("Filtrar por Deficiência:", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    f_cid = c2.text_input("Filtrar por Cidade", value="Aracaju")

    if st.button("Filtrar Base"):
        with sqlite3.connect(DB_PATH) as conn:
            query = "SELECT nome, cidade, area_atuacao, tipo_deficiencia, bio FROM profissional_pcd WHERE 1=1"
            params = []
            if f_def:
                query += f" AND tipo_deficiencia IN ({','.join(['?']*len(f_def))})"
                params.extend(f_def)
            if f_cid:
                query += " AND cidade LIKE ?"
                params.append(f"%{f_cid}%")
            
            df = pd.read_sql_query(query, conn, params=params)
            for _, t in df.iterrows():
                st.markdown(f'<div class="card-talento"><b style="color:#22D3EE; font-size:1.1rem;">{t["nome"]}</b><br><small>📍 {t["cidade"]} | {t["tipo_deficiencia"]}</small><p style="margin-top:10px;">{t["area_atuacao"]}</p><p style="color:#94A3B8; font-size:0.9rem;">{t["bio"]}</p></div>', unsafe_allow_html=True)

# --- ABA 3: CADASTRO COMPLETO (OTIMIZADO) ---
with tab_cadastro:
    st.markdown("### 📝 Entre para o Ecossistema")
    with st.form("cadastro_completo", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo*")
            email = st.text_input("E-mail Profissional*")
            area = st.text_input("Cargo/Especialidade*")
            tel = st.text_input("WhatsApp (79 9XXXX-XXXX)")
            tipo_d = st.selectbox("Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
        with c2:
            cid = st.text_input("Cidade (SE)", value="Aracaju")
            link_in = st.text_input("Link LinkedIn")
            cv_f = st.file_uploader("Currículo Original (PDF)", type=["pdf"])
            laudo_f = st.file_uploader("Laudo PCD (PDF)*", type=["pdf"])
        
        bio = st.text_area("Resumo da sua trajetória profissional*")
        
        if st.form_submit_button("🚀 CADASTRAR E GERAR CURRÍCULO"):
            if nome and email and area and laudo_f and bio:
                with st.spinner("Criptografando documentos e salvando na base..."):
                    laudo_blob = laudo_f.read()
                    cv_blob = cv_f.read() if cv_f else None
                    
                    with sqlite3.connect(DB_PATH) as conn:
                        conn.execute("""
                            INSERT INTO profissional_pcd 
                            (nome, email, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (nome, email, cid, area, tipo_d, bio, tel, link_in, cv_blob, laudo_blob))
                    
                    # Notificação em background
                    sucesso_mail = enviar_notificacao_email(nome, email, area, tipo_d, tel, bio, laudo_blob, cv_blob)
                    
                    st.success("✅ Perfil publicado com sucesso no Zequinha da Esquina!")
                    st.balloons()
                    
                    # GERADOR DE PDF PADRONIZADO
                    pdf_data = gerar_pdf_pcd({"nome": nome, "email": email, "tel": tel, "tipo_d": tipo_d, "cidade": cid, "area": area, "bio": bio})
                    st.markdown("#### 📥 Algo a mais: Seu Currículo Padronizado")
                    st.download_button("📄 Baixar Currículo Zequinha da Esquina", data=pdf_data, file_name=f"Curriculo_{nome}.pdf", mime="application/pdf")
            else:
                st.error("Por favor, preencha todos os campos obrigatórios (*) e anexe o laudo médico.")