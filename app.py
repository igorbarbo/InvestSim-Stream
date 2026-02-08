import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InvestSim Expert v6.0", layout="wide", page_icon="🛡️")

# --- FUNÇÕES DE INTELIGÊNCIA ---
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df.dropna(subset=['Ativo'])
    except:
        return pd.DataFrame(columns=['Ativo', 'QTD', 'Preço Médio'])

# --- INICIALIZAÇÃO ---
if 'df_carteira' not in st.session_state:
    st.session_state.df_carteira = carregar_dados()

# --- NAVEGAÇÃO POR ABAS ---
tab_dash, tab_radar, tab_expert, tab_risco, tab_edit = st.tabs([
    "📊 Dashboard", "🏆 Radar de Renda", "🔍 Valuation", "🛡️ Análise de Risco", "📂 Gerenciar"
])

# --- ABA 4: ANÁLISE DE RISCO (NOVIDADE) ---
with tab_risco:
    st.title("🛡️ Matriz de Correlação e Risco")
    st.write("Ativos muito parecidos aumentam seu risco. Busque cores frias (azul) para proteção.")

    if st.button("🧬 Calcular Correlação da Carteira"):
        tickers = st.session_state.df_carteira['Ativo'].unique().tolist()
        if len(tickers) > 1:
            with st.spinner("Analisando histórico de 1 ano..."):
                # Puxa histórico de fechamento de 1 ano
                precos_hist = yf.download(tickers, period="1y", progress=False)['Close']
                # Calcula a variação percentual diária
                retornos = precos_hist.pct_change().dropna()
                # Calcula a matriz de correlação
                matriz_corr = retornos.corr()

                # Gráfico de Calor (Heatmap)
                fig_corr = px.imshow(
                    matriz_corr,
                    text_auto=".2f",
                    aspect="auto",
                    color_continuous_scale='RdBu_r', # Vermelho (quente/igual) para Azul (frio/diferente)
                    zmin=-1, zmax=1,
                    title="Quem se move junto com quem?"
                )
                st.plotly_chart(fig_corr, use_container_width=True)

                st.info("""
                **Como ler este gráfico:**
                - **Próximo de 1.0 (Vermelho):** Ativos andam juntos. Se um cair, o outro provavelmente cai.
                - **Próximo de 0.0 (Branco):** Não possuem relação. Ótimo para diversificação.
                - **Próximo de -1.0 (Azul):** Proteção perfeita. Quando um cai, o outro sobe.
                """)
        else:
            st.warning("Adicione pelo menos 2 ativos para calcular a correlação.")

# --- ABA 1, 2, 3 e 5 (Mantidas as lógicas anteriores de Dashboard, Renda, Valuation e Editor) ---
with tab_dash:
    st.title("💎 Gestão Estratégica")
    # ... (Seu código de Dashboard aqui)
    if st.button("🚀 Sincronizar Patrimônio"):
        df = st.session_state.df_carteira.copy()
        tickers = df['Ativo'].unique().tolist()
        cotacao_dolar = float(yf.download("USDBRL=X", period="1d", progress=False)['Close'].iloc[-1])
        dados_mkt = yf.download(tickers, period="1d", progress=False)['Close']
        precos_dict = {t: float(dados_mkt[t].iloc[-1] if len(tickers) > 1 else dados_mkt.iloc[-1]) for t in tickers}
        df['Preço Atual'] = df['Ativo'].apply(lambda x: precos_dict.get(x, 0) * (cotacao_dolar if not x.endswith(".SA") else 1))
        df['Total'] = df['QTD'] * df['Preço Atual']
        st.metric("Patrimônio Total", f"R$ {df['Total'].sum():,.2f}")
        st.plotly_chart(px.pie(df, values='Total', names='Ativo', hole=0.4), use_container_width=True)

with tab_edit:
    st.title("📂 Gerenciar Ativos")
    df_editado = st.data_editor(st.session_state.df_carteira, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Salvar"):
        st.session_state.df_carteira = df_editado
        st.success("Dados salvos!")
        
