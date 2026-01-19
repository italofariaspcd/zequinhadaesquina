import sqlite3

def inicializar_banco_clean():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Limpeza para garantir nova estrutura
    cursor.execute('DROP TABLE IF EXISTS competencias')
    cursor.execute('DROP TABLE IF EXISTS profissional_pcd')
    cursor.execute('DROP TABLE IF EXISTS stores')

    # Estabelecimentos
    cursor.execute('''
        CREATE TABLE stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, category TEXT, city TEXT, state TEXT,
            lat REAL, lon REAL, acessivel INTEGER,
            whatsapp TEXT, abertura INTEGER, fechamento INTEGER
        )
    ''')

    # Profissionais (Estrutura Minimalista)
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

    # Competências
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
    print("✅ Banco de dados reconstruído com sucesso!")

if __name__ == "__main__":
    inicializar_banco_clean()