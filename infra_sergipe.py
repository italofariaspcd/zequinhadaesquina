import sqlite3

def configurar_banco_sergipe():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Criando tabelas com todos os campos necessários para o Recrutamento em SE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profissional_pcd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT DEFAULT 'Aracaju',
            area_atuacao TEXT,
            tipo_deficiencia TEXT,
            bio TEXT,
            telefone TEXT,
            linkedin TEXT,
            curriculo_pdf BLOB,
            laudo_pcd BLOB
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vagas (
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
    print("✅ Banco de dados sincronizado e pronto para o ecossistema SE!")

if __name__ == "__main__":
    configurar_banco_sergipe()