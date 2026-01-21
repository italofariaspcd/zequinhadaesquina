import streamlit as st
from fpdf import FPDF
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zequinha da Esquina", page_icon="♿", layout="wide")

# --- 1. ACESSIBILIDADE: VLIBRAS ---
st.components.v1.html("""
    <div vw class="enabled">
        <div vw-access-button class="active"></div>
        <div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div>
    </div>
    <script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script>
    <script>new window.VLibras.Widget('https://vlibras.gov.br/app');</script>
""", height=0)

# --- 2. FUNÇÃO: GERADOR DE PDF ---
def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho do Projeto
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(34, 211, 238) # Cor Cyan do Zequinha
    pdf.cell(200, 10, txt="Zequinha da Esquina - Currículo Profissional", ln=True, align='C')
    pdf.ln(10)
    
    # Dados Pessoais
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"NOME: {dados['nome'].upper()}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=f"Cidade: {dados['cidade']} | WhatsApp: {dados['tel']}", ln=True)
    pdf.cell(200, 8, txt=f"E-mail: {dados['email']}", ln=True)
    pdf.ln(5)
    
    # Informação de Inclusão
    pdf.set_fill_color(232, 232, 232)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, txt=f"INFORMAÇÃO PCD: {dados['tipo_d']}", ln=True, fill=True)
    pdf.ln(5)
    
    # Perfil Profissional
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="OBJETIVO / ÁREA DE ATUAÇÃO:", ln=True)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 8, txt=dados['area'], ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="RESUMO PROFISSIONAL:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, txt=dados['bio'])
    
    # Rodapé de Impacto
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, txt="Este profissional faz parte do Ecossistema Zequinha da Esquina - Sergipe.", align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    .main-header { font-size: 3rem; font-weight: 800; color: #22D3EE; text-align: center; margin-bottom: 0px; }
    .tool-card { background: #1E293B; padding: 25px; border-radius: 15px; border: 2px solid #22D3EE; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Zequinha da Esquina ♿</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8;'>Gerador de Currículo e Inclusão em Sergipe</p>", unsafe_allow_html=True)

st.divider()

# --- 4. FERRAMENTA: GERADOR DE CURRÍCULO ---
st.markdown("### 📄 Ferramenta: Criar meu Currículo Profissional")
st.write("Preencha os campos abaixo e baixe seu currículo pronto para imprimir ou enviar por WhatsApp.")

with st.container():
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Seu Nome Completo")
        email = st.text_input("Seu E-mail")
        area = st.text_input("Área de Atuação (Ex: Auxiliar Administrativo, TI, Vendas)")
    with col2:
        cidade = st.text_input("Cidade de Residência", value="Aracaju")
        tel = st.text_input("WhatsApp com DDD")
        tipo_d = st.selectbox("Tipo de Deficiência (Para fins de Cota)", ["Física", "Visual", "Auditiva", "Intelectual", "Autismo", "Múltipla"])
    
    bio = st.text_area("Conte um pouco sobre suas experiências anteriores:")
    
    if st.button("✨ GERAR E BAIXAR CURRÍCULO"):
        if nome and area and tel and email:
            dados_curriculo = {
                "nome": nome, "email": email, "area": area, 
                "cidade": cidade, "tel": tel, "tipo_d": tipo_d, "bio": bio
            }
            try:
                pdf_output = gerar_pdf(dados_curriculo)
                st.download_button(
                    label="📥 Clique aqui para baixar o PDF",
                    data=pdf_output,
                    file_name=f"Curriculo_Zequinha_{nome.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                st.success("Tudo pronto! Seu currículo foi gerado com sucesso.")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
        else:
            st.warning("Por favor, preencha as informações básicas para gerar o documento.")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.info("💡 Como gestor do projeto, os dados preenchidos aqui auxiliam na sua visibilidade no ecossistema Zequinha da Esquina.")