import random

# Lista de lojas para simular o comércio de Aracaju
lojas_seed = [
    {"name": "Panificadora Delta (13 de Julho)", "cat": "PADARIA", "lat": -10.9270, "lon": -37.0510},
    {"name": "Mercadinho do Bairro (Jardins)", "cat": "MERCADINHO", "lat": -10.9350, "lon": -37.0550},
    {"name": "Farmácia Central (Centro)", "cat": "FARMÁCIA", "lat": -10.9100, "lon": -37.0400},
    {"name": "Padaria da Praia (Atalaia)", "cat": "PADARIA", "lat": -10.9850, "lon": -37.0450}, # Longe!
    {"name": "Ferragens Silva (13 de Julho)", "cat": "CONSTRUÇÃO", "lat": -10.9260, "lon": -37.0520},
]

def generate_sql_inserts(stores):
    sql_statements = []
    for s in stores:
        # Criando o comando SQL usando a sintaxe do PostGIS para o ponto geográfico
        stmt = f"INSERT INTO stores (name, category, location) VALUES " \
               f"('{s['name']}', '{s['cat']}', ST_SetSRID(ST_MakePoint({s['lon']}, {s['lat']}), 4326));"
        sql_statements.append(stmt)
    return sql_statements

# Gerar e exibir o SQL
inserts = generate_sql_inserts(lojas_seed)

print("-- SCRIPT DE POPULAÇÃO DE DADOS MOCK (ARACAJU) --")
print("CREATE EXTENSION IF NOT EXISTS postgis;")
print("TRUNCATE TABLE stores;") # Limpa a mesa para o teste
for line in inserts:
    print(line)