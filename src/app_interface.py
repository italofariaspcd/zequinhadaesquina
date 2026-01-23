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

# --- INFRAESTRUTURA E BANCO (Mantidos conforme original) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'zequinha.db')

def init_db():
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

st.set_page_config(page_title="Zequinha | Ecossistema PCD", page_icon="♿", layout="wide")

# --- DESIGN SYSTEM PREMIUM (UI/UX OTIMIZADA) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Fundo com profundidade */
    .stApp {
        background: radial-gradient(circle at 20% 20%, #1e293b 0%, #0f172a 100%);
    }

    /* Manifesto com Design de Vidro (Glassmorphism) e Animação */
    .manifesto-container {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(12px);
        padding: 60px;
        border-radius: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 50px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        text-align: center;
    }

    .main-header {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00F2FF 0%, #7000FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
        margin-bottom: 10px;
    }

    .sub-header {
        color: #94A3B8;
        font-size: 1.4rem;
        font-weight: 400;
        margin-bottom: 30px;
    }

    .highlight { color: #00F2FF; font-weight: 700; }

    /* Cards de Talentos Estilo 'Glass-Material' */
    .card-talento {
        background: rgba(30, 41, 59, 0.4);
        padding: 30px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 25px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .card-talento:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: #00F2FF;
        background: rgba(30, 41, 59, 0.7);
        box-shadow: 0 20px 40px rgba(0, 242, 255, 0.15);
    }

    /* Tabs Futuristas */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 30px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px;
        padding: 10px 30px;
        color: #64748B;
        font-weight: 600;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: #00F2FF !important;
        color: #0F172A !important;
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.3);
    }

    /* Inputs Estilizados */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Botão de Ação Principal - Efeito Neon */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00F2FF, #006AFF) !important;
        color: white !important;
        border: none !important;
        padding: 18px 40px !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        border-radius: 15px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 10px 20px rgba(0, 106, 255, 0.3);
        width: 100%;
    }
    
    div.stButton > button:hover {
        box-shadow: 0 0 40px rgba(0, 242, 255, 0.5);
        transform: translateY(-2px);
    }

    /* Badge de Deficiência */
    .badge {
        background: linear-gradient(90deg, rgba(0,242,255,0.1), rgba(0,106,255,0.1));
        color: #00F2FF;
        border: 1px solid rgba(0,242,255,0.3);
        padding: 4px 15px;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# --- GERADOR DE PDF E EMAIL (Mantidos) ---
def gerar_pdf_pcd(dados):
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(0, 106, 255)
    pdf.cell(200, 15, txt=fix("ZEQUINHA DA ESQUINA - CURRÍCULO"), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"NOME: {fix(dados['nome'].upper())}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=fix(f"E-mail: {dados['email']} | WhatsApp: {dados['tel']}"), ln=True)
    if dados['linkedin']: pdf.cell(200, 8, txt=fix(f"LinkedIn: {dados['linkedin']}"), ln=True)
    pdf.cell(200, 8, txt=fix(f"Local: {dados['cidade']} | Deficiência: {dados['tipo_d']}"), ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=fix("RESUMO PROFISSIONAL:"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=fix(dados['bio']))
    return pdf.output(dest='S').encode('latin-1')

def enviar_notificacao_email(nome, email, area, deficiencia, tel, bio, linkedin, arquivo_laudo=None, arquivo_cv=None):
    try:
        remetente = st.secrets["EMAIL_USER"]
        senha = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["EMAIL_DESTINATARIO"]
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = f"🆕 Novo Cadastro PCD: {nome} - {area}"
        corpo = f"Nome: {nome}\nE-mail: {email}\nÁrea: {area}\nDeficiência: {deficiencia}\nWhatsApp: {tel}\nBio: {bio}"
        msg.attach(MIMEText(corpo, 'plain'))
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
        return True
    except: return False

# --- UI CONTENT ---
st.markdown(f"""
    <div class="manifesto-container">
        <p class="header"> ZEQUINA DA ESQUINA </p>
        <p class="sub-header">Transformando a <span class="highlight">Empregabilidade PCD</span> com Inteligência de Dados</p>
        <p style="font-size: 1.15rem; color: #CBD5E1; line-height: 1.8; max-width: 850px; margin: 0 auto;">
            Somos o elo tecnológico entre o talento resiliente de Sergipe e o mercado de trabalho. 
            Nossa plataforma utiliza <b>Engenharia de Dados</b> para validar habilidades e garantir 
            que a diversidade não seja apenas uma meta, mas um valor real.
        </p>
    </div>
""", unsafe_allow_html=True)

tab_busca, tab_vagas, tab_cadastro = st.tabs(["🔍 MURAL DE TALENTOS", "💼 OPORTUNIDADES", "🚀 MEU PERFIL"])

with tab_busca:
    st.markdown("<h3 style='text-align: center; color: white;'>Encontre o Talento Ideal</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        f_def = st.multiselect("Filtrar por Deficiência:", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    with c2:
        f_cid = st.text_input("Filtrar por Cidade", placeholder="Aracaju, SE")

    if st.button("ATUALIZAR BUSCA"):
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
            
            if df.empty:
                st.info("Nenhum talento disponível nesta categoria no momento.")
            else:
                col_cards = st.columns(2)
                for i, t in df.iterrows():
                    with col_cards[i % 2]:
                        st.markdown(f'''
                            <div class="card-talento">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                                    <span class="badge">{t["tipo_deficiencia"]}</span>
                                    <span style="color: #64748B; font-size: 0.8rem;">📍 {t["cidade"]}</span>
                                </div>
                                <h3 style="color: white; margin-bottom: 5px;">{t["nome"]}</h3>
                                <p style="color: #00F2FF; font-weight: 600; margin-bottom: 15px;">{t["area_atuacao"]}</p>
                                <p style="color: #94A3B8; font-size: 0.95rem; line-height: 1.6; height: 80px; overflow: hidden;">{t["bio"][:150]}...</p>
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05);">
                                    {f'<a href="{t["linkedin"]}" target="_blank" style="color: #00F2FF; text-decoration: none; font-weight: bold; font-size: 0.9rem;">CONECTAR VIA LINKEDIN →</a>' if t["linkedin"] else ''}
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)

with tab_vagas:
    st.markdown("<div style='text-align: center; padding: 50px;'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/1063/1063196.png", width=100)
    st.markdown("<h3 style='color: white;'>Vagas em Sergipe</h3><p style='color: #94A3B8;'>Estamos conectando novas empresas parceiras. Volte em breve!</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab_cadastro:
    st.markdown("<h3 style='color: white;'>Impulsione sua Carreira</h3>", unsafe_allow_html=True)
    
    with st.form("cadastro_premium"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo*")
            email = st.text_input("E-mail para Contato*")
            area = st.text_input("Área de Especialidade*")
            tel = st.text_input("WhatsApp")
        with c2:
            tipo_d = st.selectbox("Sua Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
            cid = st.text_input("Sua Cidade", value="Aracaju")
            link_in = st.text_input("Link do LinkedIn")
            cv_f = st.file_uploader("Upload de Currículo (PDF)", type=["pdf"])
            laudo_f = st.file_uploader("Upload de Laudo (Obrigatório)*", type=["pdf"])
        
        bio = st.text_area("Descreva sua jornada profissional e sonhos*")
        submit = st.form_submit_button("CRIAR MEU PERFIL AGORA")

    if submit:
        if nome and email and area and laudo_f and bio:
            with st.spinner("🚀 Lançando seu perfil ao mercado..."):
                laudo_blob = laudo_f.read()
                cv_blob = cv_f.read() if cv_f else None
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("""
                        INSERT INTO profissional_pcd 
                        (nome, email, cidade, area_atuacao, tipo_deficiencia, bio, telefone, linkedin, curriculo_pdf, laudo_pcd) 
                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (nome, email, cid, area, tipo_d, bio, tel, link_in, cv_blob, laudo_blob))
                
                st.session_state['pdf_bytes'] = gerar_pdf_pcd({"nome": nome, "email": email, "tel": tel, "tipo_d": tipo_d, "cidade": cid, "area": area, "bio": bio, "linkedin": link_in})
                st.session_state['nome_usuario'] = nome
                st.success("✨ Seu perfil agora faz parte do Ecossistema Zequinha!")
                st.balloons()
        else:
            st.error("Ops! Campos obrigatórios (*) precisam de atenção.")

    if 'pdf_bytes' in st.session_state:
        st.markdown("<div style='background: rgba(0,242,255,0.1); padding: 30px; border-radius: 20px; border: 1px dashed #00F2FF; text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: white; margin-bottom: 20px;'>Pronto para brilhar! Baixe sua versão padronizada:</h4>", unsafe_allow_html=True)
        st.download_button(
            label="📄 BAIXAR CURRÍCULO PROFISSIONAL",
            data=st.session_state['pdf_bytes'],
            file_name=f"Zequinha_CV_{st.session_state['nome_usuario']}.pdf",
            mime="application/pdf"
        )
        st.markdown("</div>", unsafe_allow_html=True)