import sqlite3

def povoar_nacional():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()

    # Reset completo para garantir o novo Schema
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
            whatsapp TEXT
        )
    ''')

    # Dados de exemplo para demonstração nacional
    lojas = [
        ('Pão & Cia - Jardins', 'PADARIA', 'Aracaju', 'SE', -10.9298, -37.0545, 1, '79999990001'),
        ('Drogasil Paulista', 'FARMÁCIA', 'São Paulo', 'SP', -23.5615, -46.6558, 1, '11999990002'),
        ('Mercado Modelo', 'MERCADINHO', 'Salvador', 'BA', -12.9691, -38.5126, 1, '71999990003'),
        ('Central da Construção', 'CONSTRUÇÃO', 'Rio de Janeiro', 'RJ', -22.9068, -43.1729, 1, '21999990004'),
        ('Panificação Pand’oro', 'PADARIA', 'Aracaju', 'SE', -10.9265, -37.0495, 1, '79999990005')
    ]

    cursor.executemany('''
        INSERT INTO stores (name, category, city, state, lat, lon, acessivel, whatsapp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', lojas)

    conn.commit()
    conn.close()
    print("✅ Banco Nacional Pronto!")

if __name__ == "__main__":
    povoar_nacional()