import streamlit as st

st.title("📈 Simulação de Investimento")

capital_inicial = st.number_input(
    "Capital inicial (R$)",
    min_value=0.0,
    value=100000.0,
    step=1000.0
)

aporte_mensal = st.number_input(
    "Aporte mensal (R$)",
    min_value=0.0,
    value=5000.0,
    step=500.0
)

taxa_mensal = st.slider(
    "Rentabilidade mensal (%)",
    min_value=0.0,
    max_value=5.0,
    value=1.0,
    step=0.1
)

meses = st.slider(
    "Período (meses)",
    min_value=1,
    max_value=120,
    value=60
)

if st.button("Simular"):
    montante = capital_inicial

    for _ in range(meses):
        montante = montante * (1 + taxa_mensal / 100) + aporte_mensal

    st.success(f"💰 Montante final: R$ {montante:,.2f}")
