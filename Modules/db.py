import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    # Adicionamos a coluna 'setor' na criação
    c.execute('''CREATE TABLE IF NOT EXISTS assets 
                 (ticker TEXT PRIMARY KEY, qtd REAL, pm REAL, setor TEXT)''')
    conn.commit()
    conn.close()

def add_asset(ticker, qtd, pm, setor):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO assets VALUES (?, ?, ?, ?)", (ticker, qtd, pm, setor))
    conn.commit()
    conn.close()

def delete_asset(ticker):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("DELETE FROM assets WHERE ticker = ?", (ticker,))
    conn.commit()
    conn.close()

def get_assets():
    conn = sqlite3.connect('portfolio.db')
    df = pd.read_sql_query("SELECT * FROM assets", conn)
    conn.close()
    return df
    
