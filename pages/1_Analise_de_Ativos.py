import streamlit as st
import yfinance as yf
import pandas as pd
from yfinance.exceptions import YFRateLimitError

st.set_page_config(page_title="Análise de Ativos", layout="wide")
st.title("📈 Análise de Ativos")

ticker = st.text_input("Ticker (ex: PETR4.SA)", value="PETR4.SA")

@st.cache_data(ttl=3600)  # cache de 1 hora (OBRIGATÓRIO)
def carregar_dados(ticker):
    ativo = yf.Ticker(ticker)
    return ativo.history(period="1y")

if ticker:
    with st.spinner("Acessando dados do Yahoo Finance..."):
        try:
            dados = carregar_dados(ticker)

            if dados.empty:
                st.warning("Nenhum dado encontrado para este ativo.")
            else:
                st.subheader(f"Desempenho de {ticker} (12 meses)")
                st.line_chart(dados["Close"])

        except YFRateLimitError:
            st.error(
                "🚫 Limite de requisições do Yahoo Finance atingido.\n\n"
                "Aguarde alguns minutos e recarregue a página."
            )

        except Exception as e:
            st.error(f"Erro ao buscar dados: {e}")
