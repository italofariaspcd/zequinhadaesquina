import sqlite3

def zerar_e_recriar_banco():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # 1. Apaga as tabelas existentes (Cuidado: apaga todos os dados!)
    print("Limpando tabelas antigas...")
    cursor.execute('DROP TABLE IF EXISTS profissional_pcd')
    cursor.execute('DROP TABLE IF EXISTS vagas')
    cursor.execute('DROP TABLE IF EXISTS competencias')

    # 2. Cria a tabela de Talentos com a estrutura correta (incluindo tipo_deficiencia)
    print("Criando nova estrutura para Sergipe...")
    cursor.execute('''
        CREATE TABLE profissional_pcd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT DEFAULT 'Aracaju',
            area_atuacao TEXT,
            tipo_deficiencia TEXT,  -- Campo crítico para o filtro
            bio TEXT,
            telefone TEXT,
            linkedin TEXT,
            curriculo_pdf BLOB,
            laudo_pcd BLOB
        )
    ''')

    # 3. Cria a tabela de Vagas
    cursor.execute('''
        CREATE TABLE vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT,
            titulo_vaga TEXT,
            cidade TEXT DEFAULT 'Aracaju',
            requisitos TEXT,
            contato_vaga TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Banco de dados zerado e pronto para novos cadastros!")

if __name__ == "__main__":
    zerar_e_recriar_banco()