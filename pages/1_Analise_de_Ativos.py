import streamlit as st
import yfinance as yf
import requests_cache
from requests import Session
from datetime import timedelta

# Configura uma sessão com cache (isso evita o Rate Limit)
# Se você pedir o mesmo ticker em menos de 1 hora, ele usa o dado salvo
session = requests_cache.CachedSession('yfinance.cache', expire_after=timedelta(hours=1))
session.headers.update({'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

st.title("🔍 Analisador B3 (Ações e FIIs)")

ticker = st.text_input("Digite o Ticker (ex: BBAS3.SA):", "PETR4.SA").upper()

if st.button("Analisar Ativo"):
    with st.spinner(f"Consultando {ticker}..."):
        try:
            # Passamos a sessão configurada para o yfinance
            ativo = yf.Ticker(ticker, session=session)
            
            # Tenta buscar os dados
            dados = ativo.history(period="1y")
            
            if not dados.empty:
                st.subheader(f"Desempenho de {ticker}")
                st.line_chart(dados['Close'])
                
                # Exibe dividendos se houver
                if not ativo.dividends.empty:
                    st.subheader("💰 Dividendos Recentes")
                    st.bar_chart(ativo.dividends.tail(10))
            else:
                st.error("Dados vazios. Verifique se o ticker está correto (ex: VALE3.SA)")
                
        except Exception as e:
            if "RateLimitError" in str(e) or "429" in str(e):
                st.error("🚨 O Yahoo Finance limitou o acesso temporariamente. Aguarde 1 minuto ou tente outro ticker.")
            else:
                st.error(f"Ocorreu um erro: {e}")
                
