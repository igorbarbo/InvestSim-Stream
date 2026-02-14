import streamlit_authenticator as stauth
import sqlite3

def carregar_credenciais():
    conn = sqlite3.connect('data/invest_v10.db')
    c = conn.cursor()
    c.execute("SELECT username, nome, senha_hash FROM usuarios")
    usuarios = c.fetchall()
    conn.close()
    
    credentials = {"usernames": {}}
    for u in usuarios:
        credentials["usernames"][u[0]] = {"name": u[1], "password": u[2]}
    return credentials

def criar_authenticator():
    credentials = carregar_credenciais()
    return stauth.Authenticate(credentials, "invest_cookie", "key_v10", 30)
    
