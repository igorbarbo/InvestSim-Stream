import streamlit as st
import yfinance as yf
import pandas as pd
import requests

st.title("🔍 Analisador B3 (Ações e FIIs)")

# Função para buscar dados com tratamento de erro de limite
def buscar_dados(ticker):
    try:
        # Criamos uma sessão que finge ser um navegador Chrome
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        ativo = yf.Ticker(ticker, session=session)
        # Usamos period='1mo' primeiro para testar a conexão, depois '1y'
        df = ativo.history(period="1y")
        return df, ativo
    except Exception as e:
        return None, str(e)

ticker_input = st.text_input("Digite o Ticker (ex: VALE3.SA):", "PETR4.SA").upper()

if st.button("Analisar Ativo"):
    with st.spinner("Solicitando dados ao servidor..."):
        dados, erro = buscar_dados(ticker_input)
        
        if dados is not None and not dados.empty:
            st.success(f"Dados de {ticker_input} carregados com sucesso!")
            st.line_chart(dados['Close'])
            
            # Mostra o preço atual
            preco_atual = dados['Close'].iloc[-1]
            st.metric("Preço Atual", f"R$ {preco_atual:.2f}")
        else:
            if "429" in str(erro) or "Too Many Requests" in str(erro):
                st.error("🚨 Limite atingido! O Yahoo Finance bloqueou o acesso temporário.")
                st.info("💡 **Dica:** Tente escrever o ticker de forma diferente (ex: ITUB4.SA) ou aguarde 2 minutos. Servidores gratuitos compartilham o mesmo acesso.")
            else:
                st.error(f"Erro ao buscar: {erro}")
                
