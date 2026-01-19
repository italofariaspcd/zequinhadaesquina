import sqlite3

def atualizar_banco_completo():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # --- 1. TABELA DE ESTABELECIMENTOS (ACESSÍVEIS) ---
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

    # --- 2. TABELA DE TALENTOS PCD (CONEXÃO SOCIAL) ---
    cursor.execute('DROP TABLE IF EXISTS profissional_pcd')
    cursor.execute('''
        CREATE TABLE profissional_pcd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT DEFAULT 'Aracaju',
            estado TEXT DEFAULT 'SE',
            bio TEXT,
            area_atuacao TEXT,
            mentor_disponivel INTEGER DEFAULT 0
        )
    ''')

    # --- 3. TABELA DE COMPETÊNCIAS (SKILLS) ---
    cursor.execute('DROP TABLE IF EXISTS competencias')
    cursor.execute('''
        CREATE TABLE competencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profissional_id INTEGER,
            competencia TEXT NOT NULL,
            nivel TEXT,
            FOREIGN KEY (profissional_id) REFERENCES profissional_pcd(id)
        )
    ''')

    # --- INSERÇÃO DE DADOS DE TESTE (POVOAMENTO) ---

    # Lojas em Aracaju e SP
    lojas = [
        ('Pão & Cia - Jardins', 'PADARIA', 'Aracaju', 'SE', -10.9298, -37.0545, 1, '79999990001', 6, 20),
        ('Farmácia Pague Menos', 'FARMÁCIA', 'Aracaju', 'SE', -10.9125, -37.0548, 1, '79999990002', 7, 22),
        ('Drogasil Paulista', 'FARMÁCIA', 'São Paulo', 'SP', -23.5615, -46.6558, 1, '11999990002', 0, 24)
    ]
    cursor.executemany('INSERT INTO stores (name, category, city, state, lat, lon, acessivel, whatsapp, abertura, fechamento) VALUES (?,?,?,?,?,?,?,?,?,?)', lojas)

    # Profissionais PCD para o Mural
    profissionais = [
        ('Ítalo', 'Aracaju', 'SE', 'Engenheiro de Dados e Especialista em Cibersegurança. Atleta de Parahalterofilismo.', 'Dados & IA', 1),
        ('Maria Silva', 'Aracaju', 'SE', 'Desenvolvedora Fullstack focada em acessibilidade web.', 'Tecnologia', 0)
    ]
    cursor.executemany('INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao, mentor_disponivel) VALUES (?,?,?,?,?,?)', profissionais)

    # Skills vinculadas ao Ítalo (ID 1)
    skills = [
        (1, 'Python', 'Sênior'),
        (1, 'SQL', 'Sênior'),
        (1, 'Cybersecurity', 'Especialista'),
        (2, 'JavaScript', 'Pleno')
    ]
    cursor.executemany('INSERT INTO competencias (profissional_id, competencia, nivel) VALUES (?,?,?)', skills)

    conn.commit()
    conn.close()
    print("✅ Banco de dados nacional e Mural de Talentos sincronizados com sucesso!")

if __name__ == "__main__":
    atualizar_banco_completo()