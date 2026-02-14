# views/gestao.py
import streamlit as st
from decimal import Decimal
from models.ativo import Ativo
from database.repository import AtivoRepository
from utils.validators import validar_ticker

def show_gestao(user_id):
    st.title("⚙️ Gerenciar Ativos")
    
    repo = AtivoRepository()
    
    tab1, tab2 = st.tabs(["📥 Adicionar", "✏️ Editar/Excluir"])
    
    with tab1:
        with st.form("add_ativo", clear_on_submit=True):
            st.subheader("➕ Novo Ativo")
            col1, col2 = st.columns(2)
            with col1:
                ticker = st.text_input("📌 Ticker", help="Ex: PETR4, MXRF11, AAPL").upper().strip()
                qtd = st.number_input("🔢 Quantidade", min_value=0.01, step=0.01, format="%.2f")
            with col2:
                pm = st.number_input("💵 Preço Médio (R$)", min_value=0.01, step=0.01, format="%.2f")
                setor = st.selectbox("🏷️ Setor", ["Ações", "FII Papel", "FII Tijolo", "ETF", "Renda Fixa", "BDR", "Internacional"])
            submitted = st.form_submit_button("💾 Salvar Ativo", use_container_width=True)
            if submitted:
                if not validar_ticker(ticker):
                    st.error("❌ Ticker inválido! Use formato B3 (PETR4) ou internacional (AAPL).")
                elif qtd <= 0 or pm <= 0:
                    st.error("❌ Quantidade e preço devem ser positivos.")
                else:
                    try:
                        ativo = Ativo(
                            ticker=ticker,
                            quantidade=Decimal(str(qtd)),
                            preco_medio=Decimal(str(pm)),
                            setor=setor
                        )
                        repo.salvar(ativo, user_id)
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
    
    with tab2:
        st.subheader("📋 Ativos Cadastrados")
        ativos = repo.carregar_por_usuario(user_id)
        if not ativos:
            st.info("📭 Nenhum ativo cadastrado.")
            return
        
        if 'editando' not in st.session_state:
            st.session_state.editando = None
        
        for ativo in ativos:
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.write(f"**{ativo['ticker']}** | {ativo['qtd']:.2f} cotas | R$ {ativo['pm']:.2f} | {ativo['setor']}")
                with col2:
                    if st.button(f"✏️", key=f"edit_{ativo['ticker']}", use_container_width=True):
                        st.session_state.editando = ativo['ticker']
                        st.rerun()
                with col3:
                    if st.button(f"🗑️", key=f"del_{ativo['ticker']}", use_container_width=True):
                        if repo.excluir(user_id, ativo['ticker']):
                            st.success(f"✅ {ativo['ticker']} excluído!")
                            st.rerun()
                
                if st.session_state.editando == ativo['ticker']:
                    with st.form(key=f"form_edit_{ativo['ticker']}"):
                        nova_qtd = st.number_input("Quantidade", value=float(ativo['qtd']))
                        novo_pm = st.number_input("Preço Médio", value=float(ativo['pm']))
                        novo_setor = st.selectbox("Setor", 
                                                 ["Ações", "FII Papel", "FII Tijolo", "ETF", "Renda Fixa", "BDR", "Internacional"],
                                                 index=["Ações", "FII Papel", "FII Tijolo", "ETF", "Renda Fixa", "BDR", "Internacional"].index(ativo['setor']))
                        col_s1, col_s2 = st.columns(2)
                        with col_s1:
                            if st.form_submit_button("Salvar"):
                                ativo_mod = Ativo(
                                    ticker=ativo['ticker'],
                                    quantidade=Decimal(str(nova_qtd)),
                                    preco_medio=Decimal(str(novo_pm)),
                                    setor=novo_setor
                                )
                                repo.salvar(ativo_mod, user_id)
                                st.session_state.editando = None
                                st.rerun()
                        with col_s2:
                            if st.form_submit_button("Cancelar"):
                                st.session_state.editando = None
                                st.rerun()
                st.divider()
