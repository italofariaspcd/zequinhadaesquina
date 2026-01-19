import sqlite3
import os
from geopy.distance import geodesic

# Caminho do banco de dados (na raiz ou pasta database)
DB_PATH = 'zequinha.db'

def setup_database():
    """
    Cria o banco de dados SQLite com suporte a acessibilidade e geolocalização.
    """
    # Conectar ao banco (se não existir, será criado)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Limpeza e Criação do Schema Evoluído
    print("--- Evoluindo Schema: Adicionando campo de Acessibilidade ---")
    cursor.execute('DROP TABLE IF EXISTS stores')
    cursor.execute('''
        CREATE TABLE stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            acessivel INTEGER DEFAULT 0, -- 1 para Sim (Acessível), 0 para Não
            whatsapp TEXT
        )
    ''')

    # 2. Mock Data de Aracaju (Incluindo dados de acessibilidade)
    # Formato: (Nome, Categoria, Lat, Lon, Acessivel, WhatsApp)
    lojas = [
        ("Panificadora Delta (13 de Julho)", "PADARIA", -10.9270, -37.0510, 1, "79999990001"),
        ("Mercadinho Jardins", "MERCADINHO", -10.9350, -37.0550, 0, "79999990002"),
        ("Ferragens Silva (13 de Julho)", "CONSTRUÇÃO", -10.9260, -37.0520, 1, "79999990003"),
        ("Farmácia Atalaia", "FARMÁCIA", -10.9850, -37.0450, 1, "79999990004"), # Longe do 13 de Julho
        ("Frutaria do Augusto Franco", "MERCADINHO", -10.9600, -37.0700, 0, "79999990005")
    ]

    cursor.executemany('''
        INSERT INTO stores (name, category, lat, lon, acessivel, whatsapp) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', lojas)

    conn.commit()
    print(f"✅ Banco de dados '{DB_PATH}' atualizado com {len(lojas)} lojas.")
    conn.close()

def buscar_vizinhos_acessiveis(lat_user, lon_user, categoria, apenas_acessiveis=False, raio_km=2.0):
    """
    Realiza a busca geoespacial com filtro opcional de acessibilidade.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query base filtrando por categoria
    query = "SELECT name, lat, lon, acessivel FROM stores WHERE category = ?"
    params = [categoria]

    # Se o usuário marcar que quer apenas lojas acessíveis (PCD)
    if apenas_acessiveis:
        query += " AND acessivel = 1"
    
    cursor.execute(query, params)
    candidatos = cursor.fetchall()
    
    resultados = []
    for nome, lat, lon, acessivel in candidatos:
        distancia = geodesic((lat_user, lon_user), (lat, lon)).km
        if distancia <= raio_km:
            status_pcd = "♿ Acessível" if acessivel == 1 else "⚠️ Não Acessível"
            resultados.append({
                "nome": nome,
                "distancia": distancia,
                "acessibilidade": status_pcd
            })
    
    conn.close()
    return sorted(resultados, key=lambda x: x['distancia'])

# --- TESTE DO SCRIPT ---
if __name__ == "__main__":
    setup_database()

    # Simulação: Usuário PCD no bairro 13 de Julho precisando de algo em uma loja acessível
    USER_LAT, USER_LON = -10.9255, -37.0500
    
    print("\n--- TESTE DE BUSCA PCD (RAIO 2KM) ---")
    resultados = buscar_vizinhos_acessiveis(USER_LAT, USER_LON, "CONSTRUÇÃO", apenas_acessiveis=True)

    for r in resultados:
        print(f"📍 {r['nome']} | Distância: {r['distancia']:.2f}km | {r['acessibilidade']}")