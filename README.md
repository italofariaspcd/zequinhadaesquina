# ♿ Zequinha da Esquina: Ecossistema de Autonomia e Empregabilidade PCD

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Gemini_AI-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

> **Zequinha da Esquina** é uma solução *Full-Stack* de impacto social que utiliza Inteligência Artificial e Engenharia de Dados para mitigar barreiras de acessibilidade urbana e profissional para Pessoas com Deficiência (PCD).

---

## 📋 Visão Geral do Projeto

Desenvolvido com foco na realidade de **Sergipe** e expansível para todo o Brasil, o projeto nasceu da necessidade de conectar profissionais PCD ao mercado de trabalho e oferecer um mapeamento dinâmico de estabelecimentos acessíveis. O sistema utiliza processamento de linguagem natural (NLP) para permitir interações via voz, garantindo acessibilidade a usuários com diferentes níveis de mobilidade.

## 🏗️ Arquitetura Técnica

O ecossistema foi projetado seguindo princípios de **Cibersegurança** e **Clean Code**:

* **Engine de IA:** Integração com o modelo `gemini-1.5-flash` para classificação de demandas em tempo real.
* **Data Layer:** Persistência em SQLite com suporte a objetos binários (BLOB) para gestão de documentos (Currículos PDF).
* **UI/UX Inclusiva:** Design System baseado em *Slate & Cyan Tech*, otimizado para alto contraste e baixa carga cognitiva.
* **Segurança:** Protocolos de sanitização de dados e integração de SOS emergencial via API de mensageria.

---

## 🚀 Funcionalidades Chave

### 1. Mural Nacional de Talentos
Vitrine profissional onde usuários cadastram perfis técnicos, redes sociais e anexam currículos. 
* **Destaque:** Sistema de download direto de PDFs e integração com WhatsApp/LinkedIn.

### 2. Localizador Acessível com Voz
Interface de busca que permite ao usuário falar sua necessidade (ex: "Onde tem uma padaria com rampa?").
* **IA:** O Gemini interpreta o áudio transcrevido e filtra categorias comerciais no banco de dados.

### 3. Módulo de Resposta a Emergências (SOS)
Botão de pânico que aciona a rede de apoio cadastrada, integrando geolocalização e mensagens automáticas.

---

## 🛠️ Configuração e Instalação

### Pré-requisitos
* Python 3.10 ou superior
* Chave de API do Google Gemini (configurada em `.streamlit/secrets.toml`)

### Guia Rápido
1.  **Clonagem do Repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/zequinhadaesquina.git](https://github.com/seu-usuario/zequinhadaesquina.git)
    cd zequinhadaesquina
    ```
2.  **Ambiente Virtual e Dependências:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
    pip install -r requirements.txt
    ```
3.  **Setup do Banco de Dados:**
    ```bash
    python povoar_nacional.py
    ```
4.  **Execução:**
    ```bash
    streamlit run src/app_interface.py
    ```

---

## 📊 Roadmap de Desenvolvimento (Gestão de Projetos)
- [x] MVP: Busca por voz e categorização via IA.
- [x] Sprint 2: Mural de Talentos e Gestão de PDFs.
- [ ] Sprint 3: Implementação de Dashboard de Analytics (Streamlit Metrics).
- [ ] Sprint 4: Geolocalização via API do Google Maps (Integração Direta).

## 🛡️ Segurança de Dados
Este projeto segue as diretrizes da LGPD para o tratamento de dados pessoais, garantindo que currículos e informações de contato sejam acessados apenas por meio da interface autorizada.

---

## 👤 Desenvolvedor
**Ítalo Farias**
* *Engenheiro de Dados & Especialista em Cibersegurança*
* *MBA em Gestão de Projetos e Metodologias Ágeis*
* *Atleta de Parahalterofilismo 🏋️‍♂️*

---
*Documentação gerada para o ecossistema @acf_aracaju e comunidade PCD Brasil.*