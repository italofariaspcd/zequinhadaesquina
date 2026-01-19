import sqlite3

def povoar_banco():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Reinicia a tabela para garantir o novo schema nacional
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

    # Dados de exemplo: Aracaju, São Paulo e Salvador
    lojas = [
        ('Pão & Cia - Jardins', 'PADARIA', 'Aracaju', 'SE', -10.9298, -37.0545, 1, '79999990001', 6, 20),
        ('Drogasil Paulista', 'FARMÁCIA', 'São Paulo', 'SP', -23.5615, -46.6558, 1, '11999990002', 0, 24),
        ('Mercado Modelo', 'MERCADINHO', 'Salvador', 'BA', -12.9691, -38.5126, 1, '71999990003', 8, 18),
        ('Panificação Pand’oro', 'PADARIA', 'Aracaju', 'SE', -10.9265, -37.0495, 1, '79999990005', 6, 21)
    ]

    cursor.executemany('''
        INSERT INTO stores (name, category, city, state, lat, lon, acessivel, whatsapp, abertura, fechamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', lojas)

    conn.commit()
    conn.close()
    print("✅ Banco de dados nacional com horários criado!")

if __name__ == "__main__":
    povoar_banco()