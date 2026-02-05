import streamlit as st
import yfinance as yf
import pandas as pd

# ------------------------------
# Configuração da página
# ------------------------------
st.set_page_config(page_title="InvestSim", layout="wide")
st.title("💰 InvestSim Low-Cost (Streamlit)")

# ------------------------------
# 1️⃣ Parâmetros do usuário
# ------------------------------
st.sidebar.header("Parâmetros do Investimento")
initial_amount = st.sidebar.number_input("Valor Inicial (R$)", value=100000, step=1000)
monthly_contribution = st.sidebar.number_input("Aporte Mensal (R$)", value=5000, step=500)
months = st.sidebar.number_input("Prazo (meses)", value=120, step=1)
target_yield = st.sidebar.slider("Meta de renda mensal (%)", 0.0, 5.0, 1.0) / 100

# ------------------------------
# 2️⃣ Carteira editável
# ------------------------------
st.sidebar.subheader("Distribuição da Carteira")
assets = [
    {"ticker": "ITUB4.SA", "weight": st.sidebar.slider("ITUB4.SA (%)", 0, 100, 30)/100},
    {"ticker": "KNRI11.SA", "weight": st.sidebar.slider("KNRI11.SA (%)", 0, 100, 30)/100},
    {"ticker": "BOVA11.SA", "weight": st.sidebar.slider("BOVA11.SA (%)", 0, 100, 40)/100},
]

# ------------------------------
# 3️⃣ Atualizar preços e dividendos via Yahoo Finance
# ------------------------------
for asset in assets:
    try:
        stock = yf.Ticker(asset["ticker"])
        hist = stock.history(period="1d")
        asset["price"] = hist['Close'][-1] if not hist.empty else 0
        div = stock.dividends.tail(12).sum() if not stock.dividends.empty else 0
        asset["yield"] = div/12 / asset["price"] if asset["price"] > 0 else 0
    except:
        asset["price"] = 0
        asset["yield"] = 0

# ------------------------------
# 4️⃣ Simulação mês a mês
# ------------------------------
data = []
total_capital = initial_amount

for month in range(1, months+1):
    monthly_income = sum([total_capital * asset['weight'] * asset['yield'] for asset in assets])
    total_capital += monthly_contribution + monthly_income
    alert = monthly_income >= total_capital * target_yield
    data.append({
        "Mês": month,
        "Patrimônio Total": round(total_capital, 2),
        "Renda Mensal": round(monthly_income, 2),
        "Alerta Meta": "✅" if alert else ""
    })

df = pd.DataFrame(data)

# ------------------------------
# 5️⃣ Resultados e gráficos
# ------------------------------
st.subheader("📊 Simulação mês a mês")
st.dataframe(df)

st.subheader("📈 Gráficos")
col1, col2 = st.columns(2)
with col1:
    st.line_chart(df.set_index("Mês")["Patrimônio Total"])
with col2:
    st.bar_chart(df.set_index("Mês")["Renda Mensal"])

# ------------------------------
# 6️⃣ Exportar CSV
# ------------------------------
st.subheader("💾 Exportar CSV")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='simulacao_investsim.csv',
    mime='text/csv'
)

# ------------------------------
# 7️⃣ Observações
# ------------------------------
st.markdown("""
**Observações:**
- Preços e dividendos atualizados via Yahoo Finance (gratuito)
- Carteira editável no sidebar
- Bola de neve: reinvestimento automático da renda
- Alertas em verde quando a renda mensal atinge a meta
- Pode adicionar novos ativos diretamente na lista `assets`
- Valores de dividendos podem variar conforme histórico da Yahoo Finance
""")
