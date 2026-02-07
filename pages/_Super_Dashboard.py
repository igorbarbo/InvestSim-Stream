# _Super_Dashboard_Visual.py

import yfinance as yf
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(page_title="InvestSim Ultra Ninja", layout="wide")
st.title("🦸‍♂️ InvestSim Ultra Ninja – Dashboard Visual")
st.markdown("📈 Máximo desempenho: Bola de Neve • Dividendos Reais • Ranking • Benchmark")

# Input de tickers
tickers_input = st.text_input("Digite os tickers separados por vírgula:", "AAPL,MSFT,GOOGL")
ativos_final = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# ========================= CACHE =========================
@st.cache_data(ttl=3600)
def get_dividendos(ticker):
    try:
        df = yf.Ticker(ticker).dividends
        df.index = pd.to_datetime(df.index)
        df = df.rename(ticker)
        return df
    except Exception as e:
        st.warning(f"Não foi possível carregar dividendos de {ticker}: {e}")
        return pd.Series(dtype='float64')

@st.cache_data(ttl=3600)
def get_preco(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="1d")
        return hist['Close'].iloc[-1] if not hist.empty else None
    except Exception:
        return None

# ========================= BOLA DE NEVE =========================
def bola_de_neve(divid_df, precos):
    reinvest = pd.DataFrame(index=divid_df.index)
    for t in divid_df.columns:
        reinvest[t] = (divid_df[t].cumsum() + precos.get(t, 0))  # seguro contra None
    return reinvest

# ========================= MAIN =========================
if ativos_final:
    dividendos_list = [get_dividendos(t) for t in ativos_final]

    if any(not df.empty for df in dividendos_list):
        df_div = pd.concat(dividendos_list, axis=1).fillna(0)

        # ====== LAYOUT: 3 COLUNAS ======
        col1, col2, col3 = st.columns([3,3,4])

        # COL1: Tabela de Dividendos
        with col1:
            st.subheader("📊 Dividendos")
            st.dataframe(df_div)

        # COL2: Dividendos por ano
        with col2:
            df_div_ano = df_div.groupby(df_div.index.year).sum()
            st.subheader("📈 Dividendos por Ano")
            st.bar_chart(df_div_ano)

        # COL3: Ranking e Alertas
        with col3:
            precos = {t: get_preco(t) for t in ativos_final}
            div_anuais = df_div.resample('Y').sum().iloc[-1]
            dividend_yield = {t: div_anuais[t]/precos.get(t, 1) for t in ativos_final}  # seguro contra None
            df_yield = pd.DataFrame.from_dict(dividend_yield, orient='index', columns=['Dividend Yield'])
            df_yield.sort_values('Dividend Yield', ascending=False, inplace=True)

            st.subheader("🏆 Ranking Dividend Yield")
            st.dataframe(df_yield.style.format("{:.2%}"))

            alert_thresh = st.slider("⚡ Alertas de Dividendos (%)", 0.5, 10.0, 3.0)
            alert_div = df_yield[df_yield['Dividend Yield'] > alert_thresh/100]
            if not alert_div.empty:
                st.warning(f"Ativos com Dividend Yield acima de {alert_thresh}%")
                st.dataframe(alert_div.style.format("{:.2%}"))

        # ====== BOLA DE NEVE ======
        df_bola = bola_de_neve(df_div, precos)
        if st.checkbox("💰 Mostrar gráfico Bola de Neve"):
            st.subheader("💰 Crescimento com Bola de Neve")
            st.line_chart(df_bola)

        # ====== BENCHMARK ======
        st.subheader("📊 Benchmark: S&P500")
        try:
            sp500 = yf.Ticker("^GSPC").history(period="1y")['Close']
            sp500_norm = sp500 / sp500.iloc[0] * 100
            st.line_chart(sp500_norm)
        except Exception:
            st.info("Não foi possível carregar dados do benchmark S&P500")
    else:
        st.warning("Não foi possível carregar dividendos para os tickers fornecidos.")
else:
    st.info("Digite pelo menos um ticker para iniciar a análise.")
