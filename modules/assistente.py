import streamlit as st
import pandas as pd
from modules.analise import analise_caro_barato

def lista_ativos_v8():
    return {
        "Renda Fixa": ["Tesouro Selic", "CDB 110% CDI", "LCI 95% IPCA"],
        "FIIs": ["MXRF11", "HGLG11", "KNRI11", "XPLG11", "CPTS11", "KNCR11", "HGBS11", "VISC11", "BRCR11"],
        "Ações": ["VALE3", "PETR4", "ITUB4", "WEGE3", "BBAS3", "PRIO3", "RAIZ4", "BBDC4", "ABEV3", "RENT3", "EQTL3", "SUZB3"],
        "ETFs": ["IVVB11", "BOVA11", "SMAL11", "PIBB11", "FIXA11"],
        "BDRs/Internacional": ["AAPL34", "GOOGL34", "MSFT34", "AMZO34", "NVDC34", "IVV", "QQQ", "SPY"]
    }

def renderizar_assistente(user_id, salvar_func):
    st.subheader("🎯 Montagem de Carteira em 3 Passos")
    
    col1, col2, col3 = st.columns(3)
    
    # Passo 1
    with col1:
        st.markdown("### 1. Perfil")
        valor_aporte = st.number_input("Valor disponível (R$)", min_value=100.0, value=1000.0)
        perfil = st.selectbox("Seu Perfil", ["Conservador", "Moderado", "Arrojado"])
    
    # Passo 2
    with col2:
        st.markdown("### 2. Alocação")
        if perfil == "Conservador":
            st.info("Sugerido: 80% Renda Fixa / 20% FIIs")
        elif perfil == "Moderado":
            st.info("Sugerido: 40% RF / 30% FIIs / 30% Ações")
        else:
            st.info("Sugerido: 20% RF / 40% Ações / 40% Int.")
            
    # Passo 3
    with col3:
        st.markdown("### 3. Escolha")
        categorias = lista_ativos_v8()
        cat_sel = st.selectbox("Categoria", list(categorias.keys()))
        ativo_sel = st.selectbox("Ativo", categorias[cat_sel])
        
        if cat_sel != "Renda Fixa":
            status, cor, desc, atual, _, _ = analise_caro_barato(ativo_sel)
            st.markdown(f"**Preço:** R$ {atual:.2f} | <span style='color:{cor}'>{status}</span>", unsafe_allow_html=True)
        
        if st.button("➕ Adicionar à Carteira"):
            salvar_func(user_id, ativo_sel, 1, 0, cat_sel) # Qtd inicial 1 para ajuste manual depois
            st.success(f"{ativo_sel} adicionado!")
          
