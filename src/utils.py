import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import st.secrets as secrets # Usando Secrets por segurança

def enviar_notificacao_pcd(nome, area, deficiencia, bio, arquivo_pdf=None):
    # Credenciais guardadas com segurança no Streamlit Secrets
    remetente = st.secrets["EMAIL_USER"]
    senha = st.secrets["EMAIL_PASSWORD"]
    destinatario = "seu-email-do-conselho@gmail.com"

    # Configuração da Mensagem
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = f"🚀 Novo Cadastro PCD: {nome} ({area})"

    corpo = f"""
    Novo profissional cadastrado no Ecossistema Zequinha SE:
    
    Nome: {nome}
    Área: {area}
    Deficiência: {deficiencia}
    Resumo: {bio}
    
    Este dado também foi salvo no banco de dados zequinha.db.
    """
    msg.attach(MIMEText(corpo, 'plain'))

    # Anexar o Laudo ou Currículo se existir
    if arquivo_pdf:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(arquivo_pdf)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename=Laudo_PCD_{nome}.pdf")
        msg.attach(part)

    # Envio via Servidor Gmail (Exemplo)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False