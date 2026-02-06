import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)  # Guarda os dados por 1 hora
def get_dados_ativo(ticker, period="1y"):
    """
    Retorna histórico diário do ativo usando yfinance.
    Corrige tickers brasileiros adicionando '.SA'.
    """
    # Adiciona .SA se for B3 e não tiver
    if len(ticker) <= 6 and not ticker.upper().endswith(".SA"):
        ticker = f"{ticker.upper()}.SA"
    else:
        ticker = ticker.upper()
    
    try:
        ativo = yf.Ticker(ticker)
        dados = ativo.history(period=period)
        
        if dados.empty:
            return pd.DataFrame()  # vazio
        return dados
    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")
        return pd.DataFrame()
