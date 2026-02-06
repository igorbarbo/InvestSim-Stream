import streamlit as st
import pandas as pd
from logic.investment import calcular_investimento, obter_taxa_cenario
from utils.formatters import format_brl

st.subheader("💰 Simulação de Investimentos")

# Inputs
perfil = st.selectbox("Perfil:", ["Conservador", "Moderado", "Agressivo"])
v_inicial = st.number_input("Inicial (R$)", value=1000.0, step=100.0)
v_mensal = st.number_input("Mensal (R$)", value=100.0, step=50.0)
v_tempo = st.slider("Anos", 1, 35, 10)
taxa = st.slider("Taxa Anual (%)", 1.0, 30.0, float(obter_taxa_cenario(perfil)))

# Calcula
df = calcular_investimento(v_inicial, v_mensal, taxa, v_tempo)

final = df["Patrimônio Total"].iloc[-1]
investido = df["Total Investido"].iloc[-1]
ganho = final - investido

c1, c2, c3 = st.columns(3)
c1.metric("Total Acumulado", format_brl(final))
c2.metric("Total Investido", format_brl(investido))
c3.metric("Ganho Total", format_brl(ganho), delta=f"{(ganho/investido)*100:.1f}%" if investido>0 else None)

st.line_chart(df.set_index("Mês")[["Patrimônio Total", "Total Investido"]])
