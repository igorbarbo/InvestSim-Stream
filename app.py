import streamlit as st
import pandas as pd

# Aqui está a mágica: importamos a lógica das pastas que você organizou
from logic.investment import simulate_investment
from logic.returns import real_return
from components.cards import display_main_metrics

# 1. Configuração Visual
st.set_page_config(page_title="InvestSim Pro", layout="wide")
st.title("💰 InvestSim: Inteligência Patrimonial")

# 2. Sidebar (Entradas de dados)
st.sidebar.header("📊 Parâmetros")
v_ini = st.sidebar.number_input("Investimento Inicial", value=1000.0)
v_mensal = st.sidebar.number_input("Aporte Mensal", value=200.0)
t_anual = st.sidebar.slider("Rentabilidade Esperada (% a.a.)", 0.0, 30.0, 10.0) / 100
inf_anual = st.sidebar.number_input("Expectativa de Inflação (% a.a.)", value=4.5) / 100
anos = st.sidebar.slider("Tempo (Anos)", 1, 40, 10)

# 3. Processamento (Lógica Modular)
meses = anos * 12
taxa_real_anual = real_return(t_anual, inf_anual)

df_nominal = simulate_investment(v_ini, v_mensal, t_anual, meses)
df_real = simulate_investment(v_ini, v_mensal, taxa_real_anual, meses)

# 4. Interface (Componentes)
tot_bruto = df_nominal['Patrimônio'].iloc[-1]
tot_real = df_real['Patrimônio'].iloc[-1]
investido = v_ini + (v_mensal * meses)

display_main_metrics(tot_bruto, tot_real, investido)

# 5. Gráfico de Área Profissional
st.subheader("📈 Evolução do Patrimônio Real")
grafico_final = pd.DataFrame({
    "Mês": df_nominal["Mês"],
    "Valor Bruto": df_nominal["Patrimônio"],
    "Poder de Compra (Real)": df_real["Patrimônio"]
}).set_index("Mês")

st.area_chart(grafico_final, color=["#1c3d5a", "#29b5e8"])
