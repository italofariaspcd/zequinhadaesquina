import sqlite3

def resetar_banco_sergipe():
    conn = sqlite3.connect('zequinha.db')
    cursor = conn.cursor()
    
    # Forçamos a exclusão da tabela antiga para criar a nova com 'tipo_deficiencia'
    cursor.execute('DROP TABLE IF EXISTS profissional_pcd')
    
    # Criando a tabela com a estrutura completa e revisada
    cursor.execute('''
        CREATE TABLE profissional_pcd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT DEFAULT 'Aracaju',
            area_atuacao TEXT,
            tipo_deficiencia TEXT,  -- A COLUNA QUE ESTAVA FALTANDO
            bio TEXT,
            telefone TEXT,
            linkedin TEXT,
            curriculo_pdf BLOB,
            laudo_pcd BLOB
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados resetado e coluna 'tipo_deficiencia' adicionada!")

if __name__ == "__main__":
    resetar_banco_sergipe()