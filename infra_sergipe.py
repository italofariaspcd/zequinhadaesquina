import sqlite3

def configurar_banco_sergipe():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Limpeza para garantir o novo Schema focado em Recrutamento
    cursor.execute('DROP TABLE IF EXISTS profissional_pcd')
    cursor.execute('''
        CREATE TABLE profissional_pcd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT DEFAULT 'Aracaju',
            area_atuacao TEXT,
            tipo_deficiencia TEXT,  -- Físico, Visual, Auditivo, Intelectual, Autismo, Múltipla
            bio TEXT,
            telefone TEXT,
            linkedin TEXT,
            curriculo_pdf BLOB,     -- Arquivo do Currículo
            laudo_pcd BLOB          -- Arquivo do Laudo Médico (Obrigatório)
        )
    ''')

    # Tabela de Vagas para Empresas de Sergipe
    cursor.execute('DROP TABLE IF EXISTS vagas')
    cursor.execute('''
        CREATE TABLE vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT NOT NULL,
            titulo_vaga TEXT NOT NULL,
            cidade TEXT DEFAULT 'Aracaju',
            requisitos TEXT,
            contato_vaga TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Schema Sergipe (Talento + Laudo) configurado com sucesso!")

if __name__ == "__main__":
    configurar_banco_sergipe()