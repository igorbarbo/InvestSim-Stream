import streamlit as st
import sys
import os

# Garante que ele ache a pasta 'logic' na raiz
sys.path.append(os.getcwd())

from logic.investment import calcular_investimento 

st.title("💰 Simulação")
v_inicial = st.number_input("Valor Inicial", 1000.0)
taxa = st.number_input("Taxa Anual (%)", 10.0) / 100
meses = st.number_input("Meses", 12)

if st.button("Calcular"):
    res = calcular_investimento(v_inicial, 0, taxa, meses)
    st.metric("Resultado Estimado", f"R$ {res:.2f}")
  
