import streamlit_authenticator as stauth
import sqlite3
import streamlit as st

def carregar_credenciais():
    """Busca os usuários cadastrados no banco de dados para o login."""
    conn = sqlite3.connect('data/invest_v10.db')
    c = conn.cursor()
    try:
        c.execute("SELECT username, nome, senha_hash FROM usuarios")
        rows = c.fetchall()
    except:
        rows = []
    conn.close()
    
    cred = {"usernames": {}}
    for r in rows:
        cred["usernames"][r[0]] = {"name": r[1], "password": r[2]}
    return cred

def criar_authenticator():
    """Instancia o objeto de autenticação compatível com a versão 0.4+."""
    cred = carregar_credenciais()
    return stauth.Authenticate(cred, "invest_cookie", "auth_key_v10_ultimate", 30)
  
