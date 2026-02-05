import streamlit as st
from utils.portfolio import PORTFOLIOS

st.title("📊 Carteiras Disponíveis")

for name, data in PORTFOLIOS.items():
    st.write(f"**{name}** — Yield médio: {data['yield']*100:.2f}% ao mês")
