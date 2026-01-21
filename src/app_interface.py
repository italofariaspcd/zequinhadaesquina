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

# --- INFRAESTRUTURA E BANCO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'zequinha.db')

def init_db():
    """Inicializa o banco de dados com suporte a LinkedIn e arquivos binários"""
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

# --- GERADOR DE PDF ---
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
    if dados['linkedin']:
        pdf.cell(200, 8, txt=fix(f"LinkedIn: {dados['linkedin']}"), ln=True)
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

# --- NOTIFICAÇÃO POR E-MAIL ---
def enviar_notificacao_email(nome, email, area, deficiencia, tel, bio, linkedin, arquivo_laudo=None, arquivo_cv=None):
    try:
        remetente = st.secrets["EMAIL_USER"]
        senha = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_DESTINATARIO"]

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = f"🆕 Novo Cadastro PCD: {nome} - {area}"

        corpo = f"""
Novo profissional cadastrado no Zequinha da Esquina:

Nome: {nome}
E-mail: {email}
LinkedIn: {linkedin if linkedin else 'Não informado'}
Área: {area}
Deficiência: {deficiencia}
WhatsApp: {tel}

Resumo Profissional:
{bio}

Os documentos originais (Laudo e CV) seguem em anexo.
        """
        msg.attach(MIMEText(corpo, 'plain'))

        for arq, label in [(arquivo_laudo, "LAUDO"), (arquivo_cv, "CV")]:
            if arq:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(arq)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={label}_{nome}.pdf')
                msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
        return True
    except: return False

# --- DESIGN SYSTEM ---
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
    .stButton > button { background-color: #22D3EE !important; color: #0F172A !important; font-weight: 700 !important; width: 100%; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# --- MANIFESTO OTIMIZADO ---
st.markdown(f"""
    <div class="manifesto-container">
        <p class="main-header">Zequinha da Esquina ♿</p>
        <p style="font-size: 1.2rem; color: #94A3B8; font-weight: 600;">Ecossistema de Autonomia e Inteligência de Dados PCD em Sergipe</p>
        <p style="font-size: 1.1rem; color: #CBD5E1; line-height: 1.8;">
            O <span class="highlight">Zequinha da Esquina</span> une tecnologia de ponta à inclusão social. 
            Utilizamos <b>Engenharia de Dados</b> para dar visibilidade aos talentos PCD de Sergipe, garantindo 
            segurança, validação técnica e autonomia real no mercado de trabalho.
        </p>
    </div>
""", unsafe_allow_html=True)

tab_busca, tab_vagas, tab_cadastro = st.tabs(["🔍 BUSCAR TALENTOS", "💼 VAGAS", "📝 MEU PERFIL"])

# --- ABA: BUSCA ---
with tab_busca:
    st.markdown("### 🤝 Mural de Talentos")
    c1, c2 = st.columns([2, 1])
    f_def = c1.multiselect("Filtrar por Deficiência:", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    f_cid = c2.text_input("Filtrar por Cidade", value="Aracaju")

    if st.button("Filtrar Base"):
        with sqlite3.connect(DB_PATH) as conn:
            query = "SELECT nome, cidade, area_atuacao, tipo_deficiencia, bio, linkedin FROM profissional_pcd WHERE 1=1"
            params = []
            if f_def:
                query += f" AND tipo_deficiencia IN ({','.join(['?']*len(f_def))})"
                params.extend(f_def)
            if f_cid:
                query += " AND cidade LIKE ?"
                params.append(f"%{f_cid}%")
            
            df = pd.read_sql_query(query, conn, params=params)
            for _, t in df.iterrows():
                st.markdown(f'''
                    <div class="card-talento">
                        <b style="color:#22D3EE;">{t["nome"]}</b><br>
                        <small>📍 {t["cidade"]} | {t["tipo_deficiencia"]}</small>
                        <p>{t["area_atuacao"]}</p>
                        {f'<a href="{t["linkedin"]}" target="_blank" style="color:#22D3EE; text-decoration:none;">🔗 LinkedIn</a>' if t["linkedin"] else ''}
                    </div>
                ''', unsafe_allow_html=True)

# --- ABA: CADASTRO ---
with tab_cadastro:
    st.markdown("### 📝 Cadastro e Gerador de Currículo")
    
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
            link_in = st.text_input("Link do LinkedIn (URL)")
            cv_f = st.file_uploader("Anexar seu Currículo Original (PDF)", type=["pdf"])
            laudo_f = st.file_uploader("Anexar Laudo Médico (PDF)*", type=["pdf"])
        
        bio = st.text_area("Resumo Profissional e Habilidades*")
        submit = st.form_submit_button("🚀 CADASTRAR")

    if submit:
        if nome and email and area and laudo_f and bio:
            with st.spinner("Processando cadastro seguro..."):
                laudo_blob = laudo_f.read()
                cv_blob = cv_f.read() if cv_f else None
                
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("""
                        INSERT INTO profissional_pcd 
                        (nome, email, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd) 
                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (nome, email, cid, area, tipo_d, bio, tel, link_in, cv_blob, laudo_blob))
                
                enviar_notificacao_email(nome, email, area, tipo_d, tel, bio, link_in, laudo_blob, cv_blob)
                
                st.session_state['pdf_bytes'] = gerar_pdf_pcd({"nome": nome, "email": email, "tel": tel, "tipo_d": tipo_d, "cidade": cid, "area": area, "bio": bio, "linkedin": link_in})
                st.session_state['nome_usuario'] = nome
                st.success("✅ Perfil publicado com sucesso!")
                st.balloons()
        else:
            st.error("Preencha todos os campos obrigatórios (*).")

    if 'pdf_bytes' in st.session_state:
        st.markdown("---")
        st.markdown("#### 📥 Algo a mais: Seu Currículo Padronizado")
        st.download_button(
            label="📄 Baixar Currículo Zequinha da Esquina",
            data=st.session_state['pdf_bytes'],
            file_name=f"Curriculo_{st.session_state['nome_usuario']}.pdf",
            mime="application/pdf"
        )

        # Coloque isso no final do arquivo, fora de qualquer aba
if st.sidebar.button("⚠️ LIMPAR TODO O BANCO"):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM profissional_pcd")
        # Reinicia o contador de ID para voltar ao 1
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='profissional_pcd'")
        conn.commit()
    st.sidebar.success("Banco de dados esvaziado!")
    st.rerun()