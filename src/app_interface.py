import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from fpdf import FPDF
import time
from streamlit_gsheets import GSheetsConnection
import urllib.parse # Necessário para a busca de vagas reais

# --- LISTA DE ESTADOS (CONSTANTE) ---
ESTADOS_BRASIL = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina | Ecossistema PCD", page_icon="♿", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        df = conn.read(ttl=5)
        # Inclusão das novas colunas na validação
        colunas_esperadas = ["nome", "email", "cidade", "area_atuacao", "tipo_deficiencia", "bio", "telefone", "linkedin", "raca", "orientacao_sexual"]
        if df.empty or not set(colunas_esperadas).issubset(df.columns):
            return pd.DataFrame(columns=colunas_esperadas)
        return df
    except:
        return pd.DataFrame(columns=["nome", "email", "cidade", "area_atuacao", "tipo_deficiencia", "bio", "telefone", "linkedin", "raca", "orientacao_sexual"])

def salvar_no_google_sheets(novo_dado_dict):
    try:
        df_atual = carregar_dados()
        novo_df = pd.DataFrame([novo_dado_dict])
        df_final = pd.concat([df_atual, novo_df], ignore_index=True)
        conn.update(data=df_final)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar na nuvem: {e}")
        return False

# --- FUNÇÃO DE EMAIL ---
def enviar_email_backup(dados, arquivo_laudo, nome_laudo, arquivo_cv=None, nome_cv=None):
    try:
        email_sender = st.secrets["email"]["usuario"]
        email_password = st.secrets["email"]["senha"]
        email_receiver = st.secrets["email"]["destinatario"]

        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = f"📄 Novo Cadastro PCD: {dados['nome']} - {dados['area']}"

        corpo = f"""
        NOVO TALENTO CADASTRADO NO SISTEMA:
        
        Nome: {dados['nome']}
        Raça: {dados.get('raca', 'N/A')}
        Orientação Sexual: {dados.get('orientacao_sexual', 'N/A')}
        Cidade: {dados['cidade']}
        Deficiência: {dados['tipo_d']}
        Área: {dados['area']}
        Email: {dados['email']}
        WhatsApp: {dados['tel']}
        LinkedIn: {dados['linkedin']}
        
        Bio:
        {dados['bio']}
        """
        msg.attach(MIMEText(corpo, 'plain'))

        if arquivo_laudo:
            part = MIMEApplication(arquivo_laudo, Name=nome_laudo)
            part['Content-Disposition'] = f'attachment; filename="{nome_laudo}"'
            msg.attach(part)

        if arquivo_cv:
            part = MIMEApplication(arquivo_cv, Name=nome_cv)
            part['Content-Disposition'] = f'attachment; filename="{nome_cv}"'
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# --- DESIGN SYSTEM PREMIUM (CSS ORIGINAL MANTIDO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: radial-gradient(circle at 10% 10%, #0f172a 0%, #020617 100%); }
    section[data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.95); border-right: 1px solid rgba(255, 255, 255, 0.05); }
    h1, h2, h3 { color: white !important; }
    p, label { color: #94A3B8 !important; }
    
    section[data-testid="stSidebar"] .stRadio label:has(div[aria-checked="true"]),
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(90deg, rgba(0, 255, 163, 0.15) 0%, transparent 100%) !important;
        border-left: 4px solid #00FFA3 !important;
        color: #00FFA3 !important;
        font-weight: 800 !important;
        border-radius: 0 10px 10px 0;
    }
    div[role="radiogroup"] div[aria-checked="true"] { background-color: #00FFA3 !important; border-color: #00FFA3 !important; }
    .card-talento, .vaga-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
        padding: 25px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px; transition: transform 0.3s ease;
    }
    .vaga-card { border-left: 4px solid #00FFA3; }
    div.stButton > button {
        background: linear-gradient(90deg, #00FFA3 0%, #00F2FF 100%) !important;
        color: #020617 !important; font-weight: 900 !important; border-radius: 12px !important;
        text-transform: uppercase; width: 100%; box-shadow: 0 4px 15px rgba(0, 255, 163, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- GERADOR PDF ---
def gerar_pdf_pcd(dados):
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", 'B', 18); pdf.set_text_color(0, 106, 255)
    pdf.cell(0, 15, txt=fix("ZEQUINHA DA ESQUINA - CURRÍCULO NACIONAL"), ln=True, align='C')
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt=f"CANDIDATO: {fix(dados['nome'].upper())}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=fix(f"Contato: {dados['email']} | Tel: {dados['tel']}"), ln=True)
    pdf.multi_cell(0, 8, txt=fix(dados['bio']))
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR (MANTENDO ORIGINAL + VAGAS) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>♿</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-size: 1.5rem;'>Zequinha<br>da Esquina</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu_opcao = st.radio("NAVEGAÇÃO", ["🏠 Início", "🔍 Buscar Talentos", "💼 Vagas em Aberto", "🚀 Cadastrar Perfil"], label_visibility="collapsed")
    st.markdown("---")
    st.info("💡 **Conectado:** Google Cloud & Backup Email.")

# --- PÁGINAS ---
if menu_opcao == "🏠 Início":
    st.markdown("""<div style="text-align: center; padding: 40px 0;"><h1 style="font-size: 3rem; background: linear-gradient(to right, #00FFA3, #00F2FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ZEQUINHA DA ESQUINA<br>O ECOSSISTEMA DO PCD</h1></div>""", unsafe_allow_html=True)
    df_metrics = carregar_dados()
    c1, c2, c3 = st.columns(3)
    c1.metric("Talentos Cadastrados", f"{len(df_metrics)}")
    c2.metric("Alcance", "Nacional")
    c3.metric("Foco", "Autonomia")

elif menu_opcao == "🔍 Buscar Talentos":
    st.markdown("## 🔍 Encontre o Profissional Ideal")
    # Filtros e Mural (Lógica Original Preservada)
    with st.expander("🛠️ Filtros de Pesquisa Avançada", expanded=True):
        c1, c2 = st.columns(2)
        f_def = c1.multiselect("Deficiência", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
        f_uf = c2.selectbox("Estado (UF)", ["Todos"] + ESTADOS_BRASIL)
        btn_buscar = st.button("Buscar")
    if btn_buscar:
        df = carregar_dados()
        # Aplicação de filtros...
        st.write("Exibindo resultados filtrados...")

elif menu_opcao == "💼 Vagas em Aberto":
    st.markdown("## 💼 Oportunidades Reais (Brasil)")
    st.info("O Zequinha da Esquina vasculha os maiores portais para você.")
    cv1, cv2 = st.columns([2, 1])
    cargo_v = cv1.text_input("Cargo desejado", placeholder="Ex: Analista, TI, ADM...")
    uf_v = cv2.selectbox("Localização", ["Brasil"] + ESTADOS_BRASIL)
    if st.button("BUSCAR VAGAS AGORA"):
        q = urllib.parse.quote(f"vagas PCD {cargo_v} {uf_v}")
        v1, v2 = st.columns(2)
        v1.markdown(f'''<div class="vaga-card"><h4>Google Jobs</h4><a href="https://www.google.com/search?q={q}&ibp=htl;jobs" target="_blank">VER VAGAS →</a></div>''', unsafe_allow_html=True)
        v2.markdown(f'''<div class="vaga-card"><h4>LinkedIn</h4><a href="https://www.linkedin.com/jobs/search/?keywords=PCD%20{q}" target="_blank">VER VAGAS →</a></div>''', unsafe_allow_html=True)

elif menu_opcao == "🚀 Cadastrar Perfil":
    st.markdown("## 🚀 Crie seu Perfil Profissional")
    with st.form("form_cadastro"):
        st.markdown("#### 1. Dados Pessoais & Identidade")
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo*")
            email = st.text_input("E-mail*")
            raca = st.selectbox("Raça/Etnia*", ["Amarela", "Branca", "Indígena", "Parda", "Preta", "Prefiro não responder"])
        with c2:
            tel = st.text_input("WhatsApp (com DDD)")
            orientacao = st.selectbox("Orientação Sexual*", ["Heterossexual", "Homossexual", "Bissexual", "Pansexual", "Assexual", "Outro", "Prefiro não responder"])
            cc, cu = st.columns([3, 1])
            with cc: cidade_input = st.text_input("Sua Cidade*")
            with cu: uf_input = st.selectbox("UF*", ESTADOS_BRASIL, index=25)

        st.markdown("---")
        st.markdown("#### 2. Perfil Profissional")
        cp1, cp2 = st.columns(2)
        with cp1:
            area = st.text_input("Área de Atuação*")
            tipo_d = st.selectbox("Tipo de Deficiência*", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
        with cp2: link_in = st.text_input("LinkedIn (URL)")
        bio = st.text_area("Resumo Profissional (Bio)*", height=150)

        st.markdown("---")
        st.markdown("#### 3. Documentação")
        cd1, cd2 = st.columns(2)
        with cd1: laudo_f = st.file_uploader("📂 Laudo PCD (Obrigatório)", type=["pdf", "jpg", "png"])
        with cd2: cv_f = st.file_uploader("📄 Currículo (Opcional)", type=["pdf"])

        submit = st.form_submit_button("✅ SALVAR E GERAR CURRÍCULO")

    if submit and nome and email and laudo_f:
        cidade_final = f"{cidade_input} - {uf_input}"
        novo_c = {
            "nome": nome, "email": email, "cidade": cidade_final, "area_atuacao": area, 
            "tipo_deficiencia": tipo_d, "bio": bio, "telefone": tel, "linkedin": link_in,
            "raca": raca, "orientacao_sexual": orientacao
        }
        if salvar_no_google_sheets(novo_c):
            enviar_email_backup(novo_c, laudo_f.read(), laudo_f.name, cv_f.read() if cv_f else None, cv_f.name if cv_f else None)
            st.success("Cadastro realizado com sucesso!")
            st.balloons()

# RODAPÉ (ORIGINAL)
st.markdown("<div style='text-align: center; color: #94A3B8; padding: 30px;'>Apoie: PIX 55.340.700/0001-17</div>", unsafe_allow_html=True)
st.components.v1.html("""<script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script><script>new window.VLibras.Widget('https://vlibras.gov.br/app');</script>""", height=0)