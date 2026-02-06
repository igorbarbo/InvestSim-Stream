import streamlit as st
import yfinance as yf

st.title("🔍 Análise de Ativos")
# Valor padrão seguro para evitar erro inicial
ticker = st.text_input("Ticker (ex: ITUB4.SA):", "PETR4.SA").upper()

if st.button("Buscar Dados"):
    with st.spinner("Conectando ao Yahoo Finance..."):
        acao = yf.Ticker(ticker)
        # Busca histórico para garantir que o DataFrame não venha vazio
        dados = acao.history(period="1y")
        
        if not dados.empty:
            st.line_chart(dados['Close'])
            st.success(f"Dados de {ticker} carregados.")
        else:
            st.error(f"Erro: Não encontramos dados para {ticker}. Verifique a internet ou o código.")
            
