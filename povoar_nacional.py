import sqlite3

def atualizar_banco_nacional():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Reset da tabela para garantir categorias padronizadas
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

    # Dados de exemplo para demonstração nacional (Categorias Padronizadas)
    lojas = [
        # ARACAJU/SE - Exemplos Reais para seu portfólio local
        ('Pão & Cia - Jardins', 'PADARIA', 'Aracaju', 'SE', -10.9298, -37.0545, 1, '79999990001', 6, 20),
        ('Farmácia Pague Menos (Centro)', 'FARMÁCIA', 'Aracaju', 'SE', -10.9125, -37.0548, 1, '79999990002', 7, 22),
        ('GBarbosa Jardins', 'MERCADINHO', 'Aracaju', 'SE', -10.9330, -37.0560, 1, '79999990003', 7, 22),
        ('Panificação Pand’oro', 'PADARIA', 'Aracaju', 'SE', -10.9265, -37.0495, 1, '79999990005', 6, 21),
        
        # SÃO PAULO/SP - Demonstração de Escala
        ('Drogasil Paulista', 'FARMÁCIA', 'São Paulo', 'SP', -23.5615, -46.6558, 1, '11999990002', 0, 24),
        ('Padaria Bella Paulista', 'PADARIA', 'São Paulo', 'SP', -23.5580, -46.6600, 1, '11999990004', 0, 24),
        
        # SALVADOR/BA
        ('Mercado Modelo', 'MERCADINHO', 'Salvador', 'BA', -12.9691, -38.5126, 1, '71999990003', 8, 18),
        ('Loja da Obra Salvador', 'CONSTRUÇÃO', 'Salvador', 'BA', -12.9700, -38.5000, 1, '71999990006', 8, 18)
    ]

    cursor.executemany('''
        INSERT INTO stores (name, category, city, state, lat, lon, acessivel, whatsapp, abertura, fechamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', lojas)

    conn.commit()
    conn.close()
    print("✅ Banco de dados nacional sincronizado com as novas categorias!")

if __name__ == "__main__":
    atualizar_banco_nacional()