import sqlite3

def inicializar_banco():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Reiniciar para garantir integridade do schema
    cursor.execute('DROP TABLE IF EXISTS competencias')
    cursor.execute('DROP TABLE IF EXISTS profissional_pcd')
    cursor.execute('DROP TABLE IF EXISTS stores')

    # 1. Estabelecimentos
    cursor.execute('''
        CREATE TABLE stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, category TEXT, city TEXT, state TEXT,
            lat REAL, lon REAL, acessivel INTEGER,
            whatsapp TEXT, abertura INTEGER, fechamento INTEGER
        )
    ''')

    # 2. Profissionais (Campos para Redes e PDF)
    cursor.execute('''
        CREATE TABLE profissional_pcd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT, estado TEXT,
            area_atuacao TEXT,
            bio TEXT,
            telefone TEXT,
            linkedin TEXT,
            instagram TEXT,
            curriculo_pdf BLOB
        )
    ''')

    # 3. Competências Técnicas
    cursor.execute('''
        CREATE TABLE competencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profissional_id INTEGER,
            competencia TEXT,
            FOREIGN KEY (profissional_id) REFERENCES profissional_pcd(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Banco de dados configurado com os novos padrões de cores e dados!")

if __name__ == "__main__":
    inicializar_banco()