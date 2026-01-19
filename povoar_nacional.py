import sqlite3

def inicializar_banco_completo():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Reiniciar estrutura para o novo padrão
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

    # 2. Profissionais (Com Redes Sociais e PDF)
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

    # 3. Competências
    cursor.execute('''
        CREATE TABLE competencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profissional_id INTEGER,
            competencia TEXT,
            FOREIGN KEY (profissional_id) REFERENCES profissional_pcd(id)
        )
    ''')

    # Dados de Exemplo (Sua Bio)
    cursor.execute('''
        INSERT INTO profissional_pcd (nome, cidade, estado, area_atuacao, bio, telefone)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('Ítalo', 'Aracaju', 'SE', 'Engenharia de Dados & Cyber', 'Especialista em Cibersegurança e Atleta de Parahalterofilismo.', '79999999999'))

    conn.commit()
    conn.close()
    print("✅ Banco de dados reconstruído com suporte a Currículos e Redes Sociais!")

if __name__ == "__main__":
    inicializar_banco_completo()