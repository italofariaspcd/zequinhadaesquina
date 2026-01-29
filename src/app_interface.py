import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from fpdf import FPDF
import time
from streamlit_gsheets import GSheetsConnection
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina | Ecossistema PCD", page_icon="♿", layout="wide")

# --- LISTA DE ESTADOS (CONSTANTE) ---
ESTADOS_BRASIL = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        df = conn.read(ttl=10)
        colunas_esperadas = [
            "nome", "email", "cidade", "area_atuacao", "tipo_deficiencia", 
            "bio", "telefone", "linkedin", "raca", "orientacao_sexual", 
            "data_aceite_lgpd", "home_office"
        ]
        
        if df.empty:
            return pd.DataFrame(columns=colunas_esperadas)
            
        for col in colunas_esperadas:
            if col not in df.columns:
                df[col] = None
                
        return df[colunas_esperadas]
    except:
        return pd.DataFrame(columns=[
            "nome", "email", "cidade", "area_atuacao", "tipo_deficiencia", 
            "bio", "telefone", "linkedin", "raca", "orientacao_sexual", 
            "data_aceite_lgpd", "home_office"
        ])

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
        msg['Subject'] = f"📄 Novo Cadastro PCD: {dados['nome']} - {dados['area_atuacao']}"

        texto_ho = "Sim" if dados.get('home_office') else "Não"

        corpo = f"""
        NOVO TALENTO CADASTRADO NO SISTEMA (LGPD ACEITO):
        
        Nome: {dados['nome']}
        Raça/Etnia: {dados.get('raca', 'N/A')}
        Orientação Sexual: {dados.get('orientacao_sexual', 'N/A')}
        Cidade: {dados['cidade']}
        Deficiência: {dados['tipo_deficiencia']}
        Área: {dados['area_atuacao']}
        Interesse em Home Office: {texto_ho}
        Email: {dados['email']}
        WhatsApp: {dados['telefone']}
        LinkedIn: {dados['linkedin']}
        Data Aceite LGPD: {dados['data_aceite_lgpd']}
        
        Bio:
        {dados['bio']}
        
        *Os arquivos do Laudo e Currículo estão em anexo.*
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
        print(f"Erro ao enviar email (verifique secrets): {e}")
        return False

# --- DESIGN SYSTEM PREMIUM (CSS MELHORADO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background: radial-gradient(circle at 10% 10%, #0f172a 0%, #020617 100%); }
    
    section[data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.95); border-right: 1px solid rgba(255, 255, 255, 0.05); }
    
    h1, h2, h3 { color: white !important; }
    p, label, .stCheckbox label { color: #94A3B8 !important; }
    
    /* MENU LATERAL DESTAQUE */
    section[data-testid="stSidebar"] .stRadio label {
        color: #94A3B8 !important; font-weight: 600 !important; padding: 15px !important;
        margin-bottom: 8px !important; transition: all 0.3s ease-in-out !important; 
        border-left: 4px solid transparent; cursor: pointer; border-radius: 0 8px 8px 0;
        background: rgba(255,255,255,0.02);
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.05); color: white !important;
    }
    section[data-testid="stSidebar"] .stRadio label:has(div[aria-checked="true"]),
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(90deg, rgba(0, 255, 163, 0.15) 0%, transparent 100%) !important;
        border-left: 4px solid #00FFA3 !important; color: #00FFA3 !important;
        font-weight: 800 !important; box-shadow: 0 0 15px rgba(0, 255, 163, 0.1);
    }
    div[role="radiogroup"] div[aria-checked="true"] { background-color: #00FFA3 !important; border-color: #00FFA3 !important; }
    
    /* CARDS */
    .card-talento, .vaga-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
        padding: 25px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px; transition: transform 0.3s ease;
    }
    .card-talento:hover { transform: translateY(-5px); border-color: #00FFA3; }
    .vaga-card { border-left: 4px solid #00F2FF; }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #1E293B !important; color: white !important; border: 1px solid #334155 !important; border-radius: 10px !important;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #00FFA3 0%, #00F2FF 100%) !important;
        color: #020617 !important; border: none !important; padding: 0.85rem 2rem !important;
        font-weight: 900 !important; border-radius: 12px !important; text-transform: uppercase;
        width: 100%; transition: all 0.3s ease !important; box-shadow: 0 4px 15px rgba(0, 255, 163, 0.3) !important;
    }
    div.stButton > button:hover { 
        box-shadow: 0 0 40px rgba(0, 255, 163, 0.7) !important; transform: scale(1.03) !important; color: black !important;
    }
    
    div[data-testid="stMetricValue"] { color: #00FFA3 !important; }
    
    /* BOTÕES DE COMPARTILHAMENTO ESTILIZADOS */
    .social-btn {
        display: flex; align-items: center; justify-content: center;
        width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 8px;
        text-decoration: none !important; font-weight: bold; font-size: 0.9rem;
        transition: transform 0.2s ease, opacity 0.2s;
    }
    .btn-whatsapp {
        background-color: #25D366; color: white !important; border: 1px solid #25D366;
    }
    .btn-linkedin {
        background-color: #0077B5; color: white !important; border: 1px solid #0077B5;
    }
    .social-btn:hover {
        opacity: 0.9; transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- GERADOR PDF ---
def gerar_pdf_pcd(dados):
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(0, 106, 255)
    pdf.cell(0, 15, txt=fix("ZEQUINHA DA ESQUINA - CURRÍCULO NACIONAL"), ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt=f"CANDIDATO: {fix(dados['nome'].upper())}", ln=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=fix(f"Contato: {dados['email']} | Tel: {dados['telefone']}"), ln=True)
    
    ho_text = "SIM" if dados.get('home_office') else "NÃO"
    pdf.cell(0, 8, txt=fix(f"Local: {dados['cidade']} | Home Office: {ho_text}"), ln=True)
    pdf.cell(0, 8, txt=fix(f"Deficiência: {dados['tipo_deficiencia']}"), ln=True)
    
    if dados.get('linkedin'):
        pdf.cell(0, 8, txt=fix(f"LinkedIn: {dados['linkedin']}"), ln=True)
        
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=fix("RESUMO & OBJETIVOS:"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=fix(dados['bio']))
    
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR (VISUAL REFORMULADO) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>♿</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-size: 1.5rem; margin-top: 0;'>Zequinha<br>da Esquina</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Cabeçalho do Menu para chamar atenção
    st.markdown("<p style='font-size: 0.8rem; font-weight: bold; color: #64748B; letter-spacing: 1px; margin-bottom: 5px;'>📍 MENU PRINCIPAL</p>", unsafe_allow_html=True)
    
    menu_opcao = st.radio("NAVEGAÇÃO", ["🏠 Início", "🔍 Buscar Talentos", "💼 Vagas em Aberto", "🚀 Cadastrar Perfil"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # SEÇÃO DE COMPARTILHAMENTO (NOVO VISUAL)
    st.markdown("<p style='text-align:center; font-size:0.9rem; font-weight:bold; margin-bottom:10px;'>📢 Espalhe a Inclusão</p>", unsafe_allow_html=True)
    
    msg_share = urllib.parse.quote("Conheça o Zequinha da Esquina! O Ecossistema de empregabilidade PCD com inteligência de dados. Acesse: https://zequinhadaesquina.streamlit.app")
    
    c_share1, c_share2 = st.columns(2)
    with c_share1:
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={msg_share}" target="_blank" class="social-btn btn-whatsapp">WhatsApp</a>', unsafe_allow_html=True)
    with c_share2:
        st.markdown(f'<a href="https://www.linkedin.com/sharing/share-offsite/?url=https://zequinhadaesquina.streamlit.app" target="_blank" class="social-btn btn-linkedin">LinkedIn</a>', unsafe_allow_html=True)

    st.markdown("---")

    with st.expander("👨‍💻 Sobre o Desenvolvedor"):
        st.markdown("""
        <div style="font-size: 0.85rem; color: #CBD5E1;">
            Desenvolvido por <b>Italo Farias</b>.<br>
            <i>Engenheiro de Dados & Paratleta.</i><br><br>
            "A tecnologia é a maior ferramenta de inclusão que existe."
        </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 **Conectado:** Google Cloud & Backup Email.")

# --- PÁGINAS ---

if menu_opcao == "🏠 Início":
    st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <h1 style="font-size: 3rem; background: linear-gradient(to right, #00FFA3, #00F2FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ZEQUINHA DA ESQUINA<br>O ECOSSISTEMA DO PCD
            </h1>
            <h3 style="color: #94A3B8; font-weight: 400; margin-top: 20px;">
                Transformando a <span style="color: #00FFA3; font-weight: 700;">Empregabilidade PCD</span> com Inteligência de Dados
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # --- MÉTRICAS ---
    total_talentos, estados_alcancados, areas_distintas = 0, 0, 0
    df_metrics = carregar_dados()
    
    if not df_metrics.empty:
        total_talentos = len(df_metrics)
        if 'area_atuacao' in df_metrics.columns: 
            areas_distintas = df_metrics['area_atuacao'].nunique()
        if 'cidade' in df_metrics.columns:
            estados = df_metrics['cidade'].apply(lambda x: str(x).split('-')[-1].strip() if '-' in str(x) else None)
            estados_alcancados = estados.nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("Talentos Cadastrados", f"{total_talentos}")
    c2.metric("Estados Alcançados", f"{estados_alcancados}")
    c3.metric("Áreas de Atuação", f"{areas_distintas}")
    
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)

    # --- SEÇÃO UX: COMO FUNCIONA (Com dica de navegação) ---
    st.markdown("""
    <div style="text-align:center;">
        <h3>🚀 Como funciona o ecossistema?</h3>
        <p style="color: #94A3B8;">Para começar, selecione uma opção no <b>Menu Lateral 👈</b></p>
    </div>
    <br>
    """, unsafe_allow_html=True)

    col_ux1, col_ux2, col_ux3 = st.columns(3)
    
    with col_ux1:
        st.info("**1. Para Talentos**\n\nCadastre seu perfil, anexe seu laudo e gere um currículo PDF profissional automaticamente. Sua vitrine para o mercado.")
    
    with col_ux2:
        st.success("**2. Visibilidade**\n\nSeus dados são validados e exibidos em uma vitrine inteligente, filtrada por habilidades, localização e tipo de deficiência.")
    
    with col_ux3:
        st.warning("**3. Conexão Direta**\n\nSem intermediários. Recrutadores encontram seu perfil e entram em contato direto via WhatsApp ou LinkedIn.")

elif menu_opcao == "🔍 Buscar Talentos":
    st.markdown("## 🔍 Encontre o Profissional Ideal")
    with st.expander("🛠️ Filtros de Pesquisa Avançada", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: f_def = st.multiselect("Tipo de Deficiência", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
        with c2: f_uf = st.selectbox("Estado (UF)", ["Todos"] + ESTADOS_BRASIL)
        with c3: f_cidade = st.text_input("Cidade", placeholder="Nome da cidade")
        
        f_remoto = st.checkbox("💻 Buscar apenas profissionais com interesse em Home Office")
        
        btn_buscar = st.button("Aplicar Filtros e Buscar", type="primary")

    if btn_buscar:
        with st.spinner("Buscando na nuvem..."):
            df = carregar_dados()
            if not df.empty:
                if f_def: df = df[df['tipo_deficiencia'].isin(f_def)]
                if f_uf != "Todos": df = df[df['cidade'].str.contains(f_uf, na=False, case=False)]
                if f_cidade: df = df[df['cidade'].str.contains(f_cidade, na=False, case=False)]
                
                if f_remoto and 'home_office' in df.columns:
                    df = df[df['home_office'] == True]
                
                if df.empty:
                    st.warning("Nenhum talento encontrado com esses filtros.")
                else:
                    st.success(f"Encontrados {len(df)} profissionais.")
                    col_cards = st.columns(2)
                    for i, t in df.iterrows():
                        icone_ho = "💻" if t.get('home_office') else ""
                        with col_cards[i % 2]:
                            st.markdown(f'''
                                <div class="card-talento">
                                    <div style="display: flex; justify-content: space-between;">
                                        <b>{t.get('nome', 'Nome')}</b>
                                        <span style="color: #00FFA3; font-size: 0.8rem;">{t.get('tipo_deficiencia', 'PCD')}</span>
                                    </div>
                                    <small style="color: #94A3B8;">{t.get('area_atuacao', 'Área')}</small><br>
                                    <small>{t.get('cidade', '')} {icone_ho}</small>
                                    <p style="font-size:0.8rem; margin-top: 10px; color: #CBD5E1;">{str(t.get('bio', ''))[:120]}...</p>
                                    {f'<a href="{t.get("linkedin")}" target="_blank" style="color:#00F2FF; text-decoration:none; font-size:0.8rem; font-weight:bold;">🔗 VER LINKEDIN</a>' if t.get("linkedin") else ''}
                                </div>
                            ''', unsafe_allow_html=True)

elif menu_opcao == "💼 Vagas em Aberto":
    st.markdown("## 💼 Oportunidades em Tempo Real (Brasil)")
    st.info("Busque vagas PCD nos maiores portais de recrutamento.")
    cv1, cv2 = st.columns([2, 1])
    cargo_v = cv1.text_input("Cargo desejado", placeholder="Ex: Analista, TI, ADM...")
    uf_v = cv2.selectbox("Estado da Vaga", ["Brasil"] + ESTADOS_BRASIL)
    
    if st.button("BUSCAR VAGAS AGORA"):
        termo = f"vagas PCD {cargo_v} {uf_v}"
        q = urllib.parse.quote(termo)
        v1, v2 = st.columns(2)
        v1.markdown(f'''<div class="vaga-card"><h4>Google Jobs</h4><p>Buscar por: <b>{termo}</b></p><a href="https://www.google.com/search?q={q}&ibp=htl;jobs" target="_blank" style="color: #00FFA3; font-weight: bold;">VER VAGAS →</a></div>''', unsafe_allow_html=True)
        v2.markdown(f'''<div class="vaga-card"><h4>LinkedIn</h4><p>Vagas recentes</p><a href="https://www.linkedin.com/jobs/search/?keywords=PCD%20{q}" target="_blank" style="color: #00FFA3; font-weight: bold;">VER VAGAS →</a></div>''', unsafe_allow_html=True)

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
        
        home_office = st.checkbox("💻 Tenho preferência por vagas 100% Home Office (Remoto)")
        bio = st.text_area("Resumo Profissional (Bio)*", height=150)

        st.markdown("---")
        st.markdown("#### 3. Documentação & LGPD")
        cd1, cd2 = st.columns(2)
        with cd1: laudo_f = st.file_uploader("📂 Laudo PCD (Obrigatório)", type=["pdf", "jpg", "png"])
        with cd2: cv_f = st.file_uploader("📄 Currículo (Opcional)", type=["pdf"])

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🛡️ Termo de Consentimento e Tratamento de Dados (LGPD) - Clique para ler", expanded=False):
            st.markdown("""
            **1. Finalidade:** Os dados coletados (incluindo laudos médicos e informações de diversidade) serão utilizados exclusivamente para a criação do seu currículo na plataforma e para conectar você a oportunidades de emprego.
            
            **2. Dados Sensíveis:** Ao concordar, você autoriza expressamente o tratamento de dados pessoais sensíveis (deficiência, raça, orientação sexual) para fins de ação afirmativa em processos seletivos (Art. 11 da Lei 13.709/2018).
            
            **3. Compartilhamento:** Seu perfil público exibirá seu nome, área, cidade e resumo. Dados de contato e laudos só serão compartilhados com recrutadores mediante sua autorização ou contato direto via plataforma.
            
            **4. Seus Direitos:** Você pode solicitar a exclusão ou alteração dos seus dados a qualquer momento enviando um email para o administrador do sistema.
            """)
        
        aceite_lgpd = st.checkbox("✅ Declaro que li e concordo com o tratamento dos meus dados pessoais sensíveis para fins de empregabilidade, conforme a LGPD.")

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("✅ SALVAR E GERAR CURRÍCULO")

    if submit:
        if nome and email and area and cidade_input and bio and laudo_f and aceite_lgpd:
            cidade_final = f"{cidade_input} - {uf_input}"
            
            tel_limpo = re.sub(r'\D', '', tel) if tel else ""

            novo_cadastro = {
                "nome": nome, "email": email, "cidade": cidade_final, "area_atuacao": area,
                "tipo_deficiencia": tipo_d, "bio": bio, "telefone": tel_limpo, "linkedin": link_in,
                "raca": raca, "orientacao_sexual": orientacao,
                "data_aceite_lgpd": time.strftime("%Y-%m-%d %H:%M:%S"),
                "home_office": home_office 
            }
            
            with st.spinner("Processando dados e registrando consentimento..."):
                salvou_sheet = salvar_no_google_sheets(novo_cadastro)
                
                laudo_bytes = laudo_f.read()
                laudo_nome = laudo_f.name
                cv_bytes = cv_f.read() if cv_f else None
                cv_nome = cv_f.name if cv_f else None
                
                enviar_email_backup(novo_cadastro, laudo_bytes, laudo_nome, cv_bytes, cv_nome)
                pdf_bytes = gerar_pdf_pcd(novo_cadastro)

                if salvou_sheet:
                    st.session_state['novo_cadastro'] = True
                    st.session_state['pdf_download'] = pdf_bytes
                    st.session_state['nome_download'] = nome
                    st.success("✅ Cadastro realizado com sucesso!")
                    st.balloons()
                else:
                    st.error("Erro ao conectar com a planilha. Tente novamente.")
        else:
            if not aceite_lgpd:
                st.error("⚠️ Para continuar, você precisa ler e aceitar o Termo de Consentimento (LGPD).")
            else:
                st.error("⚠️ Preencha os campos obrigatórios (*).")

    if st.session_state.get('novo_cadastro'):
        col_down1, col_down2, col_down3 = st.columns([1,2,1])
        with col_down2:
            st.download_button(
                "📥 BAIXAR CURRÍCULO (PDF)", 
                st.session_state['pdf_download'], 
                file_name=f"CV_{st.session_state['nome_download']}.pdf", 
                mime="application/pdf"
            )
        if st.button("Fazer novo cadastro"):
            del st.session_state['novo_cadastro']
            st.rerun()

st.markdown("""
<hr style="border: 1px solid rgba(255, 255, 255, 0.05); margin-top: 50px; margin-bottom: 20px;">
<div style="text-align: center; color: #94A3B8; font-size: 0.85rem; padding-bottom: 30px; line-height: 1.6;">
    © 2026 Zequinha da Esquina - O Ecossistema do PCD <br>
    <span style="font-size: 0.75rem; opacity: 0.7;">Powered by <b>Caju Valley Solutions</b></span>
    <br><br>
    <span style="color: #E2E8F0; border: 1px solid rgba(255, 255, 255, 0.1); padding: 5px 15px; border-radius: 20px; background: rgba(255,255,255,0.02);">
        ☕ Apoie este projeto: <strong style="color: #00FFA3;">PIX (CNPJ) 55.340.700/0001-17</strong>
    </span>
</div>
""", unsafe_allow_html=True)

st.components.v1.html("""<div vw class="enabled"><div vw-access-button class="active"></div><div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div></div><script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script><script>new window.VLibras.Widget('https://vlibras.gov.br/app');</script>""", height=0)