# --- pages/_Super_Dashboard.py ---
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
import os
import time
import pickle

from utils.finance_utils import retorno_mensal, volatilidade_anual, max_drawdown, sharpe

st.set_page_config(page_title="🦸‍♂️ InvestSim Ultra Ninja", layout="wide")
st.title("🦸‍♂️ InvestSim — Ultra Ninja Optimizado")
st.markdown("Máximo desempenho para Streamlit Cloud | Bola de Neve • Dividendos Reais • Ranking • Benchmarks")

# --- Sidebar: seleção de tickers ---
st.sidebar.header("Seleção de Ativos")
ativos_input = st.sidebar.text_area(
    "Digite os tickers separados por vírgula (ex: AAPL, MSFT, TSLA, ITUB3.SA)",
    value="AAPL, MSFT, TSLA"
)
ativos_final = [t.strip().upper() for t in ativos_input.split(",")]

# --- Função para carregar dividendos com cache e retry ---
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_dividendo_cache(ticker):
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_div.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            df = pickle.load(f)
        return df
    for attempt in range(5):
        try:
            df = yf.Ticker(ticker).dividends
            if df.empty:
                df = pd.Series(dtype=float)
            with open(cache_file, "wb") as f:
                pickle.dump(df, f)
            return df
        except Exception as e:
            time.sleep(1 + attempt*0.5)  # espera crescente
    st.warning(f"Falha ao obter dividendos de {ticker}")
    return pd.Series(dtype=float)

# --- Carregando dividendos ---
st.write("⏳ Carregando dividendos e preços históricos...")
divs_list = []
precos_list = []

for t in ativos_final:
    div = get_dividendo_cache(t)
    divs_list.append(div.rename(t))
    # Preço histórico diário últimos 5 anos
    precos = yf.download(t, period="5y", progress=False)["Adj Close"]
    precos_list.append(precos.rename(t))
    time.sleep(0.5)  # evitar rate limit

df_div = pd.concat(divs_list, axis=1)
df_precos = pd.concat(precos_list, axis=1)

st.subheader("📊 Dividendos Recentes")
st.dataframe(df_div.tail(10))

# --- Bola de neve dos dividendos ---
st.subheader("💰 Bola de Neve Acumulada")
df_bolaneve = df_div.fillna(0).cumsum()
st.line_chart(df_bolaneve)

# --- Heatmap de contribuição de dividendos ---
st.subheader("🔥 Heatmap de Dividendos por Ativo")
df_heat = df_div.fillna(0).reset_index().melt(id_vars="Date", var_name="Ticker", value_name="Dividendo")
heatmap = alt.Chart(df_heat).mark_rect().encode(
    x='Date:T',
    y='Ticker:N',
    color='Dividendo:Q'
).properties(width=800, height=300)
st.altair_chart(heatmap, use_container_width=True)

# --- Métricas financeiras ---
st.subheader("📈 Métricas de Performance")
st.write("Retorno Mensal")
st.dataframe(retorno_mensal(df_precos).tail(5))

st.write("Volatilidade Anual")
st.dataframe(volatilidade_anual(df_precos))

st.write("Max Drawdown")
st.dataframe(max_drawdown(df_precos))

st.write("Sharpe Ratio")
st.dataframe(sharpe(df_precos))

# --- Ranking de dividendos ---
st.subheader("🏆 Ranking de Dividendos Acumulados")
ranking = df_div.sum().sort_values(ascending=False)
st.bar_chart(ranking)

# --- Benchmarks: Ibov e S&P500 ---
st.subheader("📊 Benchmarks")
benchmarks = {"^BVSP": "IBOV", "^GSPC": "S&P500"}
bench_list = []
for sym, name in benchmarks.items():
    data = yf.download(sym, period="5y", progress=False)["Adj Close"].rename(name)
    bench_list.append(data)
df_bench = pd.concat(bench_list, axis=1)
st.line_chart(df_bench)

st.success("✅ Dashboard carregado com sucesso! Ultra Ninja nível 5 🚀")
