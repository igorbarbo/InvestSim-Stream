# Modules/auth.py
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth

def carregar_credenciais():
    conn = sqlite3.connect('invest_v8.db')
    c = conn.cursor()
    c.execute("SELECT username, nome, senha_hash FROM usuarios")
    usuarios = c.fetchall()
    conn.close()
    
    credentials = {"usernames": {}}
    for u in usuarios:
        credentials["usernames"][u[0]] = {
            "name": u[1],
            "password": u[2]
        }
    return credentials

def criar_authenticator():
    credentials = carregar_credenciais()
    # Use uma chave secreta fixa (pode ser qualquer string)
    COOKIE_KEY = "chave_super_secreta_123"
    
    authenticator = stauth.Authenticate(
        credentials,
        "invest_app_cookie",
        COOKIE_KEY,
        30
    )
    return authenticator
