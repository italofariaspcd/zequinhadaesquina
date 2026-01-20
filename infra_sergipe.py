import sqlite3

def inicializar_sergipe():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Limpeza para novo padrão Sergipe
    cursor.execute('DROP TABLE IF EXISTS vagas')
    cursor.execute('DROP TABLE IF EXISTS profissional_pcd')
    cursor.execute('DROP TABLE IF EXISTS competencias')

    # 1. Tabela de Profissionais (Talentos de SE)
    cursor.execute('''
        CREATE TABLE profissional_pcd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT DEFAULT 'Aracaju',
            area_atuacao TEXT,
            bio TEXT,
            telefone TEXT,
            linkedin TEXT,
            curriculo_pdf BLOB
        )
    ''')

    # 2. Tabela de Vagas (Oportunidades em SE)
    cursor.execute('''
        CREATE TABLE vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT NOT NULL,
            titulo_vaga TEXT NOT NULL,
            cidade TEXT DEFAULT 'Aracaju',
            requisitos TEXT,
            contato TEXT
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

    conn.commit()
    conn.close()
    print("✅ Ecossistema Sergipe configurado com sucesso!")

if __name__ == "__main__":
    inicializar_sergipe()