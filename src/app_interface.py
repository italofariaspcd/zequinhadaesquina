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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'zequinha.db')

st.set_page_config(page_title="Zequinha da Esquina | Sergipe", page_icon="♿", layout="wide")

# --- NOVO: GERADOR DE PDF (ALGO A MAIS) ---
def gerar_pdf_pcd(dados):
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(34, 211, 238)
    pdf.cell(200, 15, txt=fix("ZEQUINHA DA ESQUINA - CURRÍCULO"), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"NOME: {fix(dados['nome'].upper())}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=fix(f"E-mail: {dados['email']} | WhatsApp: {dados['tel']}"), ln=True)
    pdf.cell(200, 8, txt=fix(f"Deficiência: {dados['tipo_d']} | Local: {dados['cidade']}"), ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=fix("RESUMO PROFISSIONAL:"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=fix(dados['bio']))
    return pdf.output(dest='S').encode('latin-1')

# --- FUNÇÃO DE E-MAIL (OTIMIZADA) ---
def enviar_notificacao_email(nome, email, area, deficiencia, tel, bio, arquivo_laudo=None):
    try:
        remetente = st.secrets["EMAIL_USER"]
        senha = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_DESTINATARIO"]

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = f"🆕 Novo Cadastro PCD: {nome}"

        corpo = f"""
        Olá, Gestor. Um novo talento acaba de entrar no ecossistema:

        Nome: {nome}
        E-mail: {email}
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

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
        return True
    except:
        return False

# --- DESIGN E ACESSIBILIDADE ---
st.components.v1.html("""
    <div vw class="enabled"><div vw-access-button class="active"></div><div vw-plugin-wrapper></div></div>
    <script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script>
    <script>new window.VLibras.Widget('https://vlibras.gov.br/app');</script>
""", height=0)

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    .manifesto-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 40px; border-radius: 20px; border: 1px solid #334155; margin-bottom: 30px;
    }
    .main-header { font-size: 3rem; font-weight: 800; color: #22D3EE; margin-bottom: 5px; }
    .highlight { color: #22D3EE; font-weight: 700; }
    .card-talento { background: #1E293B; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- MANIFESTO MELHORADO ---
st.markdown(f"""
    <div class="manifesto-container">
        <p class="main-header">Zequinha da Esquina ♿</p>
        <p style="font-size: 1.2rem; color: #94A3B8; font-weight: 600;">Ecossistema de Autonomia e Inteligência de Dados PCD em Sergipe</p>
        <p style="font-size: 1.1rem; color: #CBD5E1; line-height: 1.8;">
            O <span class="highlight">Zequinha da Esquina</span> transcende a tecnologia; é um compromisso com a dignidade. 
            Utilizamos <b>Engenharia de Dados</b> para conectar o talento invisível de Sergipe às oportunidades reais. 
            Nossa plataforma garante validação técnica, segurança da informação e, acima de tudo, o 
            <b>protagonismo do profissional com deficiência</b> no mercado de trabalho.
        </p>
    </div>
""", unsafe_allow_html=True)

tab_busca, tab_vagas, tab_cadastro = st.tabs(["🔍 BUSCAR TALENTOS", "💼 VAGAS", "📝 MEU PERFIL"])

# --- ABA 1: BUSCA (OTIMIZADA COM SEGURANÇA SQL) ---
with tab_busca:
    st.markdown("### 🤝 Mural de Talentos")
    c1, c2 = st.columns([2, 1])
    f_def = c1.multiselect("Deficiência:", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    f_cid = c2.text_input("Cidade", value="Aracaju")

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
                st.markdown(f'<div class="card-talento"><b style="color:#22D3EE;">{t["nome"]}</b><br><small>📍 {t["cidade"]} | {t["tipo_deficiencia"]}</small><p>{t["area_atuacao"]}</p></div>', unsafe_allow_html=True)

# --- ABA 3: CADASTRO (OTIMIZADA) ---
with tab_cadastro:
    st.markdown("### 📝 Cadastro e Gerador de Currículo")
    with st.form("cadastro_zequinha", clear_on_submit=False):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo*")
        email = c1.text_input("E-mail Profissional*")
        area = c1.text_input("Cargo/Especialidade*")
        tel = c1.text_input("WhatsApp")
        cid = c2.text_input("Cidade (SE)", value="Aracaju")
        tipo_d = c2.selectbox("Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
        laudo_f = c2.file_uploader("Laudo PCD (PDF)*", type=["pdf"])
        bio = st.text_area("Resumo Profissional*")
        
        if st.form_submit_button("🚀 CADASTRAR E GERAR PDF"):
            if nome and email and area and laudo_f:
                laudo_blob = laudo_f.read()
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("INSERT INTO profissional_pcd (nome, cidade, area_atuacao, tipo_deficiencia, bio, telefone, laudo_pcd) VALUES (?,?,?,?,?,?,?)",
                                 (nome, cid, area, tipo_d, bio, tel, laudo_blob))
                
                enviar_notificacao_email(nome, email, area, tipo_d, tel, bio, laudo_blob)
                
                st.success("✅ Perfil publicado com sucesso!")
                
                # Gerador de PDF
                pdf_data = gerar_pdf_pcd({"nome": nome, "email": email, "tel": tel, "tipo_d": tipo_d, "cidade": cid, "area": area, "bio": bio})
                st.download_button("📄 Baixar meu Currículo Pronto", data=pdf_data, file_name=f"Curriculo_{nome}.pdf", mime="application/pdf")
            else:
                st.error("Preencha todos os campos com (*).")