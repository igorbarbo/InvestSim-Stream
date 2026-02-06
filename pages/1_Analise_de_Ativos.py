import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Análise", layout="wide")
st.title("🔍 Análise de Ativos")

ticker = st.text_input("Digite o ticker (ex: PETR4.SA):", "VALE3.SA")
if st.button("Buscar Dados"):
    with st.spinner("Carregando..."):
        dados = yf.Ticker(ticker).history(period="1y")
        st.line_chart(dados['Close'])
        st.success(f"Dados de {ticker} atualizados!")
      
