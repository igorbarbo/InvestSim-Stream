import streamlit as st
from logic.market_data import get_dados_ativo
st.subheader("📈 Análise de Ativos")

ticker = st.text_input("Ticker (ex: PETR4)", value="PETR4")

if ticker:
    with st.spinner("Buscando dados do ativo..."):
        dados = get_dados_ativo(ticker)

    if dados.empty:
        st.error("❌ Não foi possível obter dados do ativo no momento.")
    else:
        st.line_chart(dados["Close"])
