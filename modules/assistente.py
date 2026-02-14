import streamlit as st
from modules.analise import analise_caro_barato

def renderizar_assistente(user_id, salvar_func):
    ativos = {
        "FIIs": ["MXRF11", "HGLG11", "KNRI11", "XPLG11"],
        "Ações": ["VALE3", "PETR4", "ITUB4", "WEGE3", "BBAS3"],
        "BDRs": ["AAPL34", "GOOGL34", "NVDC34"]
    }
    st.markdown("### 🎯 Assistente de Alocação")
    cat = st.selectbox("Categoria", list(ativos.keys()))
    tick = st.selectbox("Ativo", ativos[cat])
    
    status, cor, desc, atual, _, _ = analise_caro_barato(tick)
    st.markdown(f"**Status:** <span style='color:{cor}'>{status}</span> (R$ {atual:.2f})", unsafe_allow_html=True)
    
    if st.button("Salvar na Carteira"):
        salvar_func(user_id, tick, 1, atual, cat)
        st.success("Adicionado!")
        
