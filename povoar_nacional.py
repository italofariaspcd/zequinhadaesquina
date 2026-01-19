import sqlite3

def resetar_e_povoar():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Limpeza Total
    cursor.execute('DROP TABLE IF EXISTS stores')
    cursor.execute('DROP TABLE IF EXISTS profissional_pcd')
    cursor.execute('DROP TABLE IF EXISTS competencias')

    # Criação das Tabelas
    cursor.execute('''CREATE TABLE stores (id INTEGER PRIMARY KEY, name TEXT, category TEXT, city TEXT, state TEXT, lat REAL, lon REAL, acessivel INTEGER, whatsapp TEXT, abertura INTEGER, fechamento INTEGER)''')
    cursor.execute('''CREATE TABLE profissional_pcd (id INTEGER PRIMARY KEY, nome TEXT, cidade TEXT, estado TEXT, bio TEXT, area_atuacao TEXT)''')
    cursor.execute('''CREATE TABLE competencias (id INTEGER PRIMARY KEY, profissional_id INTEGER, competencia TEXT, nivel TEXT, FOREIGN KEY (profissional_id) REFERENCES profissional_pcd(id))''')

    # Dados Iniciais (Aracaju)
    lojas = [
        ('Pão & Cia - Jardins', 'PADARIA', 'Aracaju', 'SE', -10.9298, -37.0545, 1, '79999990001', 6, 20),
        ('Farmácia Pague Menos', 'FARMÁCIA', 'Aracaju', 'SE', -10.9125, -37.0548, 1, '79999990002', 7, 22)
    ]
    cursor.executemany('INSERT INTO stores (name, category, city, state, lat, lon, acessivel, whatsapp, abertura, fechamento) VALUES (?,?,?,?,?,?,?,?,?,?)', lojas)

    # Cadastro do Ítalo
    cursor.execute("INSERT INTO profissional_pcd (nome, cidade, estado, bio, area_atuacao) VALUES (?,?,?,?,?)", 
                   ('Ítalo', 'Aracaju', 'SE', 'Engenheiro de Dados e Atleta de Parahalterofilismo.', 'Engenharia de Dados'))
    p_id = cursor.lastrowid
    skills = [(p_id, 'Python'), (p_id, 'SQL'), (p_id, 'Cibersegurança')]
    cursor.executemany('INSERT INTO competencias (profissional_id, competencia) VALUES (?,?)', skills)

    conn.commit()
    conn.close()
    print("✅ Banco de dados nacional pronto para uso!")

if __name__ == "__main__":
    resetar_e_povoar()