import sqlite3
import os

db_path = 'zequinha.db'

print(f"--- Verificando: {os.path.abspath(db_path)} ---")

if not os.path.exists(db_path):
    print("❌ ERRO: O arquivo zequinha.db NÃO EXISTE nesta pasta!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificando tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()
    print(f"Tabelas encontradas: {tabelas}")

    # Verificando dados
    try:
        cursor.execute("SELECT id, nome FROM profissional_pcd")
        dados = cursor.fetchall()
        if dados:
            print(f"✅ DADOS ENCONTRADOS ({len(dados)} registros):")
            for linha in dados:
                print(f"   ID: {linha[0]} | Nome: {linha[1]}")
        else:
            print("⚠️ O arquivo existe, mas a tabela profissional_pcd está VAZIA.")
    except Exception as e:
        print(f"❌ Erro ao ler tabela: {e}")
    
    conn.close()