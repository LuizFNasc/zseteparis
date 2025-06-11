import sqlite3
from datetime import datetime

# Criação do banco, se não existir
def criar_banco():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            nome TEXT,
            email TEXT,
            telefone TEXT,
            tipo TEXT,
            quimica TEXT,
            problema TEXT,
            objetivo TEXT,
            recomendacao TEXT
        )
    """)
    conn.commit()
    conn.close()

# Salva novo lead no banco
def salvar_lead(nome, email, telefone, tipo, quimica, problema, objetivo, recomendacao):
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO leads (data_hora, nome, email, telefone, tipo, quimica, problema, objetivo, recomendacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nome, email, telefone, tipo, quimica, problema, objetivo, recomendacao))
    conn.commit()
    conn.close()

# Retorna todos os leads
def carregar_leads():
    conn = sqlite3.connect("leads.db")
    df = None
    try:
        df = conn.execute("SELECT * FROM leads").fetchall()
    finally:
        conn.close()
    return df

# Valida login básico
def autenticar(usuario, senha):
    return usuario == "admin" and senha == "1234"  # Altere isso!
