import sqlite3
import requests

def importar_todas_cidades():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()

    # Mantemos a estrutura robusta que você definiu para o projeto
    cursor.execute('DROP TABLE IF EXISTS stores')
    cursor.execute('''
        CREATE TABLE stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            acessivel INTEGER NOT NULL,
            whatsapp TEXT,
            abertura INTEGER,
            fechamento INTEGER
        )
    ''')

    # Consumindo a API oficial do IBGE para pegar todos os municípios
    print("🛰️ Coletando cidades do IBGE...")
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    response = requests.get(url)
    municipios = response.json()

    # Preparamos uma lista para inserção em lote (Best Practice de Engenharia de Dados)
    dados_para_inserir = []
    
    # Nota: Como ainda não temos o crawler de lojas, vamos inserir 
    # um "Ponto de Apoio" genérico em cada cidade para teste do seu MVP.
    for m in municipios:
        nome_cidade = m['nome']
        sigla_uf = m['microrregiao']['mesorregiao']['UF']['sigla']
        
        # Simulando um ponto de apoio acessível padrão por cidade
        dados_para_inserir.append((
            f"Ponto de Apoio PCD - {nome_cidade}", 
            "MERCADINHO", 
            nome_cidade, 
            sigla_uf, 
            0.0, 0.0, # Coordenadas seriam obtidas via Maps API futuramente
            1, 
            "00000000000", 
            8, 18
        ))

    cursor.executemany('''
        INSERT INTO stores (name, category, city, state, lat, lon, acessivel, whatsapp, abertura, fechamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', dados_para_inserir)

    conn.commit()
    conn.close()
    print(f"✅ Sucesso! {len(dados_para_inserir)} cidades cadastradas no Zequinha Nacional.")

if __name__ == "__main__":
    importar_todas_cidades()