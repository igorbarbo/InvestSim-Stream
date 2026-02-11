import streamlit as st
import plotly.express as px
from datetime import datetime
import sys
import os

# Ajuste de path para módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_engine import fetch_data, sync_prices
from src.analytics import process_metrics, convert_to_usd
from src.ai_agent import ask_ai
from src.backtesting import run_backtest

# --- FASE 3: SISTEMA DE LOGIN ---
def check_auth():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    
    if not st.session_state.auth:
        st.title("🔒 Terminal Igorbarbo V5 Pro")
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("Acessar Terminal"):
            if user == "igor" and pw == "123": # Edite suas credenciais aqui
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Acesso negado.")
        st.stop()

check_auth()

# --- INTERFACE PRINCIPAL ---
st.set_page_config(page_title="Terminal V5 | Pro", layout="wide")
st.sidebar.title("Configurações")
if st.sidebar.button("Sair / Logout"):
    st.session_state.auth = False
    st.rerun()

df_raw = fetch_data()

if df_raw is not None:
    if "df_p" not in st.session_state:
        with st.spinner("Sincronizando Mercado..."):
            st.session_state.df_p = sync_prices(df_raw)
            st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")

    df, rent_real, total = process_metrics(st.session_state.df_p)
    total_usd = convert_to_usd(total)

    # Header de Nível Institucional
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PATRIMÔNIO (BRL)", f"R$ {total:,.2f}")
    c2.metric("EQUITY (USD)", f"$ {total_usd:,.2f}")
    c3.metric("RENTABILIDADE MWA", f"{rent_real:.2f}%")
    c4.metric("STATUS", "CONECTADO", delta=st.session_state.last_sync)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 PERFORMANCE", "🧪 BACKTESTING", "🤖 IA ADVISOR", "🎯 RADAR"])

    with tab1:
        fig = px.treemap(df, path=['Ativo'], values='Patrimônio',
                         color='Valorização %', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Simulação Histórica (vs Ibovespa)")
        if st.button("Rodar Backtesting 12 Meses"):
            df_b = run_backtest(df)
            if df_b is not None:
                st.line_chart(df_b)
                ret_c = (df_b["Minha Carteira"].iloc[-1] - 1) * 100
                ret_i = (df_b["Ibovespa"].iloc[-1] - 1) * 100
                st.write(f"**Resultado:** Carteira ({ret_c:.1f}%) vs Ibov ({ret_i:.1f}%)")

    with tab3:
        st.subheader("💬 Inteligência Gemini 2.0")
        pergunta = st.chat_input("Ex: Qual o risco da minha carteira hoje?")
        if pergunta:
            resposta = ask_ai(pergunta, df)
            st.write(resposta)

    with tab4:
        st.subheader("🎯 Prioridade de Aporte")
        st.dataframe(df[['Ativo', 'Peso', 'Prioridade']].sort_values('Prioridade', ascending=False), use_container_width=True)

else:
    st.info("Conecte sua planilha para começar.")
    
