import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'zequinha.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS profissional_pcd (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    cidade TEXT,
    area_atuacao TEXT NOT NULL,
    tipo_deficiencia TEXT NOT NULL,
    bio TEXT NOT NULL,
    telefone TEXT,
    linkedin TEXT,
    curriculo_pdf BLOB,
    laudo_pcd BLOB NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()

print("✅ Banco de dados criado com sucesso!")
