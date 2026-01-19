import sqlite3

def povoar_nacional_com_horarios():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()

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
            abertura INTEGER, -- Hora (0-23)
            fechamento INTEGER -- Hora (0-23)
        )
    ''')

    # Exemplo: Lojas em Aracaju e SP com horários variados
    lojas = [
        ('Pão & Cia - Jardins', 'PADARIA', 'Aracaju', 'SE', -10.9298, -37.0545, 1, '79999990001', 6, 20),
        ('Drogasil Paulista', 'FARMÁCIA', 'São Paulo', 'SP', -23.5615, -46.6558, 1, '11999990002', 0, 24), # 24h
        ('Mercado Modelo', 'MERCADINHO', 'Salvador', 'BA', -12.9691, -38.5126, 1, '71999990003', 8, 18),
        ('Farmácia 24h 13 de Julho', 'FARMÁCIA', 'Aracaju', 'SE', -10.9240, -37.0515, 1, '79999990006', 0, 24)
    ]

    cursor.executemany('''
        INSERT INTO stores (name, category, city, state, lat, lon, acessivel, whatsapp, abertura, fechamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', lojas)

    conn.commit()
    conn.close()
    print("✅ Banco Nacional com Horários Atualizado!")

if __name__ == "__main__":
    povoar_nacional_com_horarios()