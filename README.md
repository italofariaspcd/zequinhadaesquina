# Zequinha da Esquina - Hub de Comércio Local 🏠🚀

## 📌 Sobre o Projeto
O **Zequinha da Esquina** é uma plataforma de hiper-proximidade desenhada para digitalizar o comércio de bairro. Diferente de grandes marketplaces, o foco aqui é a **disponibilidade em tempo real** e o fortalecimento da economia local, permitindo que moradores encontrem produtos a poucos metros de distância.

## 🎯 Objetivo
Reduzir a fricção entre a necessidade do consumidor e o estoque do lojista vizinho, utilizando tecnologia para responder à pergunta: *"Quem aqui perto tem o que eu preciso agora?"*

## ✨ Funcionalidades Principais (MVP)

### 👥 Para o Morador
- **Busca por Proximidade:** Localização via GPS para listar lojas num raio de até 5km.
- **Botão "Alguém Tem?":** Sistema de broadcast onde o usuário solicita um item e lojistas da categoria recebem um alerta para responder.
- **Vitrine Digital:** Visualização de produtos e ofertas do dia sem sair de casa.
- **Direct para WhatsApp:** Integração direta para fechar a compra ou tirar dúvidas.

### 🏪 Para o Lojista
- **Gestão de Inventário Simples:** Cadastro rápido de produtos via mobile.
- **Painel de Demandas:** Recebimento de notificações de usuários procurando produtos da sua categoria.
- **Status de Funcionamento:** Controle de loja aberta/fechada em tempo real.

## 🛠️ Stack Tecnológica Sugerida
- **Frontend:** Flutter ou React Native (Cross-platform).
- **Backend:** Python (FastAPI ou Django) ou Node.js.
- **Banco de Dados:** PostgreSQL com extensão PostGIS (para consultas geoespaciais).
- **Cache/Real-time:** Redis ou Firebase para as notificações do "Alguém Tem?".
- **Infra:** Docker para padronização do ambiente.

## 📈 Roadmap de Desenvolvimento

- [ ] **Fase 1:** Definição da Arquitetura e Modelagem do Banco de Dados.
- [ ] **Fase 2:** Desenvolvimento do MVP (Fluxo de busca e Perfil do Lojista).
- [ ] **Fase 3:** Implementação do sistema de notificações Push ("Alguém Tem?").
- [ ] **Fase 4:** Piloto em um bairro específico para coleta de métricas.

## 🤝 Como Contribuir
1. Faça um **Fork** do projeto.
2. Crie uma **Branch** para sua feature (`git checkout -b feature/NovaFeature`).
3. Dê um **Commit** nas suas alterações (`git commit -m 'Add NovaFeature'`).
4. Faça um **Push** para a Branch (`git push origin feature/NovaFeature`).
5. Abra um **Pull Request**.

---
Produzido com foco em: **Italo Lopes de Farias.**

## ⚖️ Regras de Engajamento (O "Alguém Tem?")

Para garantir a eficiência da plataforma, aplicamos as seguintes regras:

1. **Raio de Alcance:** As solicitações são disparadas inicialmente para um raio de **2km**. 
2. **Time-to-Response (TTR):** - O lojista tem até **5 minutos** para responder e garantir o selo de "Atendimento Flash".
   - Após **15 minutos**, a solicitação expira para aquele lojista para não poluir o painel.
3. **Limite de Ofertas:** O usuário visualiza apenas as **3 primeiras respostas** positivas. Isso incentiva a agilidade do comércio local.
4. **Ranking de Bairro:** Lojistas com maior taxa de conversão e velocidade ganham o status de "Destaque do Bairro", aparecendo no topo das buscas sem custo adicional.

## 🧠 Camada de Inteligência Artificial
O app utiliza Processamento de Linguagem Natural (NLP) para:
- **Auto-Categorização:** O usuário descreve o que precisa em linguagem natural e a IA direciona a notificação para os lojistas corretos.
- **Identificação de Urgência:** Priorizar pedidos que denotem emergência (ex: "remédio", "vazamento").
- **Sugestões Inteligentes:** Se um usuário busca por "carne", a IA sugere também "carvão" de uma loja de conveniência próxima.


Campo,Tipo,Descrição
id,UUID (PK),Identificador único.
name,VARCHAR,Nome do usuário.
email,VARCHAR,Login/Comunicação.
location,GEOMETRY(Point),Última localização capturada (opcional).

Campo,Tipo,Descrição
id,UUID (PK),Identificador único.
owner_id,FK (users),Relacionamento com o usuário gestor.
name,VARCHAR,Nome fantasia.
category,ENUM,"Padaria, Farmácia, Construção, etc."
address_coords,GEOMETRY(Point),Latitude/Longitude indexada (GIST).
whatsapp,VARCHAR,Número para o link direto.
is_open,BOOLEAN,Status em tempo real.




== Criar um app para o comércio local é uma excelente iniciativa, pois o segredo do sucesso hoje em dia não é competir com gigantes como Amazon ou Mercado Livre, mas sim oferecer o que eles não conseguem: proximidade, rapidez e senso de comunidade.

Aqui estão quatro conceitos de aplicativos, divididos por nichos e dores específicas:

1. O "Zequinha da Esquina" (Hub de Tudo)
A ideia aqui é ser o "Shopping Center Digital" do bairro. Muitas vezes o morador não sabe que a loja de ferragens a duas quadras tem o parafuso que ele precisa.

Diferencial: Um motor de busca focado em estoque local.

Funcionalidades:

Vitrine digital de produtos por categoria (padaria, farmácia, pet shop).

Botão "Chamar no WhatsApp" integrado para cada lojista.

Sistema de entrega colaborativa (motoboys do bairro que atendem todas as lojas do app).

2. "Clube de Vantagens do Bairro" (Fidelidade Coletiva)
Em vez de cada loja ter seu cartãozinho de papel, o app centraliza a fidelidade do bairro todo.

Diferencial: Gamificação e união. Se eu compro no café e na livraria local, ganho pontos que posso trocar em qualquer loja parceira.

Funcionalidades:

QR Code para validar compras.

Ranking de "Morador do Mês" (quem mais apoia o comércio local ganha prêmios).

Notificações push de "Oferta Relâmpago" baseadas na geolocalização do usuário.

3. "Agenda Local" (Serviços e Agendamentos)
Focado em prestadores de serviço (manicure, barbeiro, eletricista, aulas de yoga).

Diferencial: Resolver o caos da agenda e a dificuldade de encontrar profissionais de confiança perto de casa.

Funcionalidades:

Agendamento direto no app com integração de calendário.

Sistema de Avaliações Verificadas (apenas vizinhos reais podem avaliar).

Pagamento antecipado ou sinal para evitar "bolos".

4. "Sustenta Bairro" (Combate ao Desperdício)
Inspirado em modelos de sucesso na Europa, focado em padarias, quitandas e restaurantes.

Diferencial: Sustentabilidade e preço baixo.

Funcionalidades:

Sacola Surpresa: No final do dia, o lojista monta sacolas com produtos que vencem logo por um preço muito reduzido (ex: 70% de desconto).

Aviso de "Pão Quente": Padarias avisam quando a fornada saiu para atrair fluxo imediato.

Qual o melhor modelo de negócio?
Para que o app seja viável, você pode seguir estes caminhos:

Mensalidade Fixa: O lojista paga um valor baixo (ex: R$ 50,00/mês) para estar na vitrine.

Taxa de Transação: Se a venda ocorrer dentro do app, você fica com uma pequena porcentagem.

Anúncios Impulsionados: A loja paga para aparecer no topo da lista durante o final de semana.

Dica de Ouro: Comece pequeno. Escolha um bairro ou um condomínio grande para validar a ideia antes de tentar expandir para a cidade inteira.

Gostou de algum desses caminhos? Se quiser, eu posso te ajudar a detalhar as funcionalidades principais (MVP) para a ideia que você mais curtiu.



Componente,Status,Detalhes
Nome,✅ Definido,Zequinha da Esquina
Logo/Identidade,✅ Definido,"Estilo amigável, popular e acolhedor."
Diferencial (IA),✅ Definido,Motor de NLP para categorização automática de pedidos.
Regras de Negócio,✅ Definido,"Raio de 2km, resposta em 5min, ranking de lojistas."
Estrutura de Dados,✅ Definido,Tabelas geoespaciais (PostGIS) para busca por proximidade.


Esta é a parte onde o seu "eu" Engenheiro de Dados assume o controle. O objetivo aqui é garantir que a mensagem saia do celular do usuário e chegue ao lojista certo em milissegundos, com o menor custo computacional possível.

Como vamos usar aquele script de IA/NLP que criamos, o pipeline precisa ser reativo.

🛠️ Desenho da Arquitetura (Data Flow)
Podemos dividir o fluxo em 4 etapas principais:

1. Ingestão (O Gatilho)
Origem: Mobile App (Frontend).

Payload: Um JSON contendo user_id, texto_da_demanda e coordenadas_gps.

Transporte: API Gateway (FastAPI) recebendo a requisição via POST.

2. Processamento e Enriquecimento (O Cérebro)
Aqui entra o seu script Python.

Passo A (NLP): O texto passa pela função classificar_demanda_local. Se o usuário diz "pão de sal", a IA devolve a tag PADARIA.

Passo B (Geo-Query): O sistema consulta o PostgreSQL/PostGIS para buscar todas as stores que tenham category = 'PADARIA' e estejam dentro do ST_DWithin de 2km do usuário.

3. Orquestração de Notificações (O Broadcast)
Fila de Mensagens: Para não travar o banco, enviamos a lista de IDs de lojistas para um Redis ou RabbitMQ.

Push Notification: O serviço de notificações (Firebase Cloud Messaging) dispara o alerta para os celulares dos lojistas selecionados.

4. Sink (Persistência e Auditoria)
Toda essa transação é gravada na tabela broadcast_requests para que possamos gerar métricas depois (ex: Qual bairro de Aracaju mais pede pão às 17h?).

📊 Diagrama de Fluxo (Mermaid)
Você pode copiar este código e colar no seu README.md (o GitHub renderiza automaticamente):

Snippet de código

graph LR
    A[Usuário faz pedido] --> B(API FastAPI)
    B --> C{IA Classifier}
    C -- "Tag: PADARIA" --> D[PostGIS Query]
    D -- "Raio 2km" --> E[Lista de Lojistas]
    E --> F[Firebase Push]
    F --> G[Celular do Lojista]
    
    subgraph "Camada de Dados"
    C
    D
    end
🐍 O Próximo Nível do Script Python
Para o seu pipeline, o script anterior precisa agora de uma "saída" para o banco de dados. Veja como ficaria a lógica de integração:

Python

def processar_pipeline_demanda(user_id, lat, long, texto):
    # 1. Classifica com IA
    classificacao = classificar_demanda_local(texto)
    
    if classificacao["status"] == "sucesso":
        categoria = classificacao["notificar_categorias"][0]
        
        # 2. Simulação de Query Geoespacial
        sql_query = f"""
        SELECT id, device_token FROM stores 
        WHERE category = '{categoria}' 
        AND ST_DWithin(geom, ST_MakePoint({long}, {lat}), 2000);
        """
        
        # 3. Log para o Engenheiro de Dados
        print(f"PIPELINE: Buscando {categoria} num raio de 2km de ({lat}, {long})")
        print(f"SQL GERADO: {sql_query}")
        
        return {"status": "disparado", "categoria": categoria}
    
    return {"status": "erro", "motivo": "IA não identificou categoria"}
💡 O que podemos fazer agora?
Para avançar nessa arquitetura, o que você prefere:

Modelagem de BI: Pensar em quais dashboards você, como dono da plataforma, gostaria de ver (ex: calor de demandas por bairro em Aracaju).

Web Scraping de Início: Criar um script para extrair dados básicos de lojas de um bairro de Aracaju no Google Maps para testar o seu banco de dados.

Qual dessas frentes de dados te anima mais agora?


## 🛠️ Como rodar o ambiente de dados (Local)

Para testar o motor de busca sem necessidade de Docker ou servidores externos:

1. Instale as dependências:
   ```bash
   pip install geopy