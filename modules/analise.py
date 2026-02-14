import yfinance as yf
import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def buscar_dados(ticker):
    try:
        t = yf.Ticker(f"{ticker}.SA")
        hist = t.history(period="5y")
        divs = t.dividends
        return hist, divs
    except:
        return pd.DataFrame(), pd.Series()

def analise_caro_barato(ticker):
    hist, _ = buscar_dados(ticker)
    if hist.empty: return "🔵 SEM DADOS", "#808080", "Erro", 0, 0, 0
    
    atual = hist['Close'].iloc[-1]
    media_12m = hist['Close'].tail(252).mean()
    p20 = np.percentile(hist['Close'], 20)
    p80 = np.percentile(hist['Close'], 80)
    
    score = np.clip((p80 - atual) / (p80 - p20) * 100, 0, 100)
    
    if atual <= p20: return "🟢 OPORTUNIDADE!", "#00FF00", "Preço em mínima histórica (P20).", atual, media_12m, score
    if atual >= p80: return "🔴 CARO!", "#FF4444", "Preço em máxima (P80). Risco de queda.", atual, media_12m, score
    return "🟡 NEUTRO", "#D4AF37", "Preço equilibrado.", atual, media_12m, score

def preco_teto_bazin(ticker, dy_desejado=0.06):
    _, divs = buscar_dados(ticker)
    if divs.empty: return 0.0, 0.0
    soma_divs = divs.tail(12).sum()
    return (soma_divs / dy_desejado), soma_divs
    
