import streamlit as st
import plotly.express as px
from datetime import datetime
import sys
import os

# --- BLINDAGEM DE CAMINHO (Resolve o ImportError) ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.data_engine import fetch_data, sync_prices
    from src.analytics import process_metrics
    from src.ai_agent import ask_ai
except ImportError as e:
    st.error(f"Erro de Módulo: {e}. Verifique se a pasta 'src' e o arquivo '__init__.py' existem.")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Terminal Igorbarbo Pro", layout="wide", page_icon="⚡")

# Estilo CSS para Cards Neon e Esconder Menu Lateral (Reforço)
st.markdown("""
    <style>
        [data-testid="stMetricValue"] { font-size: 28px; color: #00ff88; }
        .main { background-color: #0e1117; }
        div[data-testid="stExpander"] { border: 1px solid #262730; }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("⚡ Terminal Igorbarbo | Enterprise")
st.markdown("---")

# --- LÓGICA DE DADOS ---
df_raw = fetch_data()

if df_raw is not None:
    # Auto-Sincronização: Se não tem dados no estado, busca agora
    if "df_p" not in st.session_state:
        with st.spinner("🚀 Sincronizando com a B3..."):
            st.session_state.df_p = sync_prices(df_raw)
            st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")

    # Se a sincronização deu certo, mostra o Dashboard
    if st.session_state.df_p is not None:
        df, rent_real, total = process_metrics(st.session_state.df_p)

        # MÉTRICAS PRINCIPAIS (Cards)
        c1, c2, c3 = st.columns(3)
        c1.metric("PATRIMÔNIO TOTAL", f"R$ {total:,.2f}")
        c2.metric("RENTABILIDADE REAL (MWA)", f"{rent_real:.2f}%")
        c3.metric("ÚLTIMA SINCRONIZAÇÃO", st.session_state.last_sync)

        # ABAS DO SISTEMA
        tab1, tab2, tab3 = st.tabs(["📊 PERFORMANCE", "🤖 IA ADVISOR", "🎯 PRIORIDADES"])

        with tab1:
            st.subheader("Mapa de Calor do Patrimônio")
            fig = px.treemap(df, path=[px.Constant("Carteira"), 'Ativo'], values='Patrimônio',
                             color='Valorização %', color_continuous_scale='RdYlGn',
                             color_continuous_midpoint=0)
            fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("💬 Consultoria Estratégica")
            pergunta = st.chat_input("Dúvida sobre a alocação?")
            if pergunta:
                with st.spinner("Analisando dados..."):
                    resposta = ask_ai(pergunta, df)
                    st.info(f"**Pergunta:** {pergunta}")
                    st.write(resposta)

        with tab3:
            st.subheader("⚖️ Radar de Aporte")
            st.write("Ativos com maior **Prioridade** são aqueles que estão baratos (queda) e com pouco peso na carteira.")
            df_sort = df[['Ativo', 'Valorização %', 'Peso', 'Prioridade']].sort_values(by='Prioridade', ascending=False)
            st.dataframe(df_sort.style.background_gradient(subset=['Prioridade'], cmap='Greens'), use_container_width=True)
            
    else:
        st.error("Erro ao sincronizar preços do Yahoo Finance. Tente novamente em instantes.")
else:
    st.error("❌ Erro: Não foi possível ler a planilha do Google Sheets.")

# --- FOOTER ---
if st.button("🔄 Forçar Atualização"):
    st.session_state.clear()
    st.rerun()
    
