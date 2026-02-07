import streamlit as st
import yfinance as yf

# Configuração da página
st.set_page_config(page_title="Simulador InvestSim", layout="wide")

st.title("📊 Simulador de Investimentos (yfinance)")

# Entrada do usuário
ticker = st.text_input("Digite o código da ação (ex: PETR4.SA, VALE3.SA, AAPL):", "PETR4.SA")

if ticker:
    try:
        # Busca os dados
        acao = yf.Ticker(ticker)
        dados = acao.history(period="1y")

        if not dados.empty:
            # Mostra o preço atual
            preco_atual = dados['Close'].iloc[-1]
            st.metric(label=f"Preço Atual de {ticker}", value=f"R$ {preco_atual:.2f}")

            # Gráfico de fechamento
            st.subheader("Evolução do Preço (Último 1 ano)")
            st.line_chart(dados['Close'])
        else:
            st.warning("Nenhum dado encontrado para este código. Verifique se digitou corretamente (lembre-se do .SA para ações brasileiras).")
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
      
