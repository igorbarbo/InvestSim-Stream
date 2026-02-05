import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Importa lógica
from logic.investment import simulate_investment
from logic.returns import real_return
from components.cards import display_main_metrics

st.set_page_config(page_title="InvestSim", layout="wide")
st.title("Simulador de Investimentos 🚀")

# Input do usuário
initial_amount = st.number_input("Valor Inicial (R$)", min_value=0.0, value=1000.0)
monthly_contrib = st.number_input("Contribuição Mensal (R$)", min_value=0.0, value=100.0)
annual_rate = st.number_input("Retorno Anual (%)", min_value=0.0, value=10.0)
years = st.number_input("Anos", min_value=1, max_value=50, value=10)

# Simula investimento
future_value = simulate_investment(initial_amount, monthly_contrib, annual_rate/100, years)
real_future_value = real_return(future_value, inflation_rate=0.04, years=years)  # inflação 4% como exemplo

# Mostra métricas
display_main_metrics(future_value, real_future_value)

# Gráfico de evolução
months = np.arange(0, years*12+1)
values = [simulate_investment(initial_amount, monthly_contrib, annual_rate/100, m/12) for m in months]
df = pd.DataFrame({"Mês": months, "Valor Investido (R$)": values})

chart = alt.Chart(df).mark_line(point=True).encode(
    x="Mês",
    y="Valor Investido (R$)"
).properties(title="Evolução do Investimento ao Longo do Tempo")
st.altair_chart(chart, use_container_width=True)
