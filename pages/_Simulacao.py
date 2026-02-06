import streamlit as st
from logic.investment import calcular_investimento

st.title("💰 Simulação de Investimento")
v_ini = st.number_input("Valor Inicial", 1000.0)
taxa = st.number_input("Taxa Anual (%)", 10.0) / 100
meses = st.number_input("Meses", 12)

if st.button("Calcular"):
    try:
        res = calcular_investimento(v_ini, 0, taxa, meses)
        st.metric("Resultado Estimado", f"R$ {res:,.2f}")
    except Exception as e:
        st.error(f"Erro no cálculo: {e}")
        
