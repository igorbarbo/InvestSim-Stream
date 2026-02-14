import streamlit as st
import pandas as pd
import yfinance as ticker_data # Exemplo usando yfinance

class PrecoService:
    @staticmethod
    @st.cache_data(ttl=900) # 15 minutos de cache
    def buscar_cotacao_atual(ticker):
        """Busca o preço atual de um ativo com proteção de cache."""
        try:
            stock = ticker_data.Ticker(f"{ticker}.SA")
            info = stock.fast_info
            return info['last_price']
        except Exception as e:
            st.error(f"Erro ao buscar cotação de {ticker}: {e}")
            return 0.0

    @staticmethod
    @st.cache_data(ttl=3600) # Cache de 1 hora para dados históricos
    def buscar_historico(ticker, period="1y"):
        stock = ticker_data.Ticker(f"{ticker}.SA")
        return stock.history(period=period)
        
