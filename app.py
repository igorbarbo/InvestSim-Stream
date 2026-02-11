import streamlit as st
import plotly.express as px
from datetime import datetime
import sys
import os
import logging

# 1. Observabilidade (Fase 2)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajuste de Caminhos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.data_engine import fetch_data, sync_prices
    from src.analytics import process_metrics
    from src.ai_agent import ask_ai
except ImportError as e:
    st.error(f"Erro de Módulo: {e}")
    st.stop()

st.set_page_config(page_title="Terminal Igorbarbo V5 Pro", layout="wide", page_icon="⚡")

# 2. Persistência de Sessão (Fase 1 - Step 3)
if "ai_calls" not in st.session_state:
    st.session_state.ai_calls = 0

# UI Style
st.markdown("<style>[data-testid='stMetricValue'] { color: #00ff88; font-family: monospace; }</style>", unsafe_allow_html=True)

st.title("⚡ Terminal Igorbarbo | Institutional V5")
st.markdown("---")

df_raw = fetch_data()

if df_raw is not None:
    # 3. Cache de sincronização para evitar erro 429
    if "df_p" not in st.session_state:
        with st.spinner("🔄 Sincronizando Mercado..."):
            st.session_state.df_p = sync_prices(df_raw)
            st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")

    df, rent_real, total = process_metrics(st.session_state.df_p)

    # Dashboard de Métricas Ponderadas
    c1, c2, c3 = st.columns(3)
    c1.metric("CAPITAL ALOCADO", f"R$ {total:,.2f}")
    c2.metric("RENTABILIDADE MWA", f"{rent_real:.2f}%")
    c3.metric("ÚLTIMO SYNC", st.session_state.last_sync)

    tab1, tab2, tab3 = st.tabs(["📊 PERFORMANCE", "🤖 IA ADVISOR", "🎯 MOTOR DE APORTE"])

    with tab1:
        fig = px.treemap(df, path=['Ativo'], values='Patrimônio',
                         color='Valorização %', color_continuous_scale='RdYlGn',
                         color_continuous_midpoint=0)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # 4. Controle de IA (Fase 2 - Step 5)
        st.subheader("💬 Gemini 2.0 Flash Pro")
        if st.session_state.ai_calls >= 15:
            st.warning("⚠️ Limite de consultas diárias atingido (Quota Control).")
        else:
            pergunta = st.chat_input("Dúvida estratégica?")
            if pergunta:
                st.session_state.ai_calls += 1
                logger.info(f"Pergunta: {pergunta} | Call #{st.session_state.ai_calls}")
                with st.spinner("Analisando notícias e carteira..."):
                    resposta = ask_ai(pergunta, df)
                    st.write(resposta)

    with tab3:
        st.subheader("⚖️ Ranking de Prioridade de Aporte")
        # Mostrando o Motor Decisional em ação
        st.dataframe(
            df[['Ativo', 'Valorização %', 'Peso', 'Prioridade']]
            .sort_values('Prioridade', ascending=False)
            .style.background_gradient(cmap='Greens', subset=['Prioridade']),
            use_container_width=True
        )
else:
    st.warning("Aguardando Google Sheets...")
    
