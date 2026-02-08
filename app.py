import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import numpy as np

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="InvestSim Expert v7.0", layout="wide", page_icon="📈")

# Estilo para os Cards de Métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #00ff88; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE INTELIGÊNCIA ---
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df.dropna(subset=['Ativo'])
    except:
        return pd.DataFrame(columns=['Ativo', 'QTD', 'Preço Médio'])

def buscar_multiplos(tickers):
    dados = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            if '11' in t and not t.startswith('IVVB'):
                v = info.get('priceToBook', 0)
                dados[t] = {'val': v, 'tipo': 'P/VP'}
            else:
                v = info.get('forwardPE', info.get('trailingPE', 0))
                dados[t] = {'val': v, 'tipo': 'P/L'}
        except:
            dados[t] = {'val': 0, 'tipo': 'N/A'}
    return dados

# --- 3. INICIALIZAÇÃO DO ESTADO ---
if 'df_carteira' not in st.session_state:
    st.session_state.df_carteira = carregar_dados()

# --- 4. NAVEGAÇÃO POR ABAS ---
tab_dash, tab_radar, tab_expert, tab_risco, tab_edit = st.tabs([
    "📊 Dashboard", "🏆 Radar de Renda", "🔍 Valuation", "🛡️ Risco/Correlação", "📂 Gerenciar"
])

# --- ABA 1: DASHBOARD ---
with tab_dash:
    st.title("💎 Gestão Estratégica de Patrimônio")
    aporte = st.sidebar.number_input("Aporte deste Mês (R$)", value=3000.0)
    
    if st.button("🔄 Sincronizar Mercado"):
        df = st.session_state.df_carteira.copy()
        tickers = df['Ativo'].unique().tolist()
        
        with st.spinner("Atualizando cotações..."):
            dolar = float(yf.download("USDBRL=X", period="1d", progress=False)['Close'].iloc[-1])
            precos = yf.download(tickers, period="1d", progress=False)['Close']
            
            p_dict = {t: float(precos[t].iloc[-1] if len(tickers) > 1 else precos.iloc[-1]) for t in tickers}
            df['Preço Atual'] = df['Ativo'].apply(lambda x: p_dict.get(x, 0) * (dolar if not x.endswith(".SA") else 1))
            df['Patrimônio'] = df['QTD'] * df['Preço Atual']
            
            total = df['Patrimônio'].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Patrimônio Total", f"R$ {total:,.2f}")
            c2.metric("Meta de Renda (0,8%)", f"R$ {total * 0.008:,.2f}")
            c3.metric("Dólar hoje", f"R$ {dolar:,.2f}")
            
            st.plotly_chart(px.pie(df, values='Patrimônio', names='Ativo', hole=0.5, title="Alocação Real"), use_container_width=True)

# --- ABA 2: RADAR DE RENDA ---
with tab_radar:
    st.title("🏆 Dividendos e Eficiência (YoC)")
    if st.button("💰 Calcular Fluxo de Caixa"):
        df_r = st.session_state.df_carteira.copy()
        for t in df_r['Ativo'].unique():
            divs = yf.Ticker(t).dividends
            # Correção 'YE' para versões novas do Pandas conforme seus LOGS
            df_r.loc[df_r['Ativo']==t, 'Div_Anual'] = divs.tail(365).sum() if not divs.empty else 0
        
        df_r['Renda_Mes'] = (df_r['QTD'] * df_r['Div_Anual']) / 12
        df_r['YoC'] = (df_r['Div_Anual'] / df_r['Preço Médio']) * 100
        
        st.metric("Renda Mensal Estimada", f"R$ {df_r['Renda_Mes'].sum():,.2f}")
        st.dataframe(df_r[['Ativo', 'QTD', 'YoC', 'Renda_Mes']].style.format({'YoC': '{:.2f}%', 'Renda_Mes': 'R$ {:.2f}'}))

# --- ABA 3: VALUATION ---
with tab_expert:
    st.title("🔍 Inteligência de Compra (Valuation)")
    if st.button("🧠 Analisar Preço Justo"):
        indicadores = buscar_multiplos(st.session_state.df_carteira['Ativo'].unique())
        for t, ind in indicadores.items():
            val, tipo = ind['val'], ind['tipo']
            with st.expander(f"Análise {t}"):
                if tipo == "P/VP":
                    status = "🟢 Barato" if val < 0.98 else "🔴 Caro" if val > 1.05 else "🟡 Justo"
                else:
                    status = "🟢 Barato" if 0 < val < 12 else "🔴 Caro" if val > 20 else "🟡 Justo"
                st.write(f"**Métrica:** {tipo} | **Valor:** {val:.2f}")
                st.subheader(status)

# --- ABA 4: RISCO ---
with tab_risco:
    st.title("🛡️ Matriz de Correlação")
    if st.button("🧬 Gerar Mapa de Calor"):
        tickers = st.session_state.df_carteira['Ativo'].unique().tolist()
        hist = yf.download(tickers, period="1y", progress=False)['Close'].pct_change().dropna()
        st.plotly_chart(px.imshow(hist.corr(), text_auto=".2f", color_continuous_scale='RdBu_r'), use_container_width=True)

# --- ABA 5: EDITOR ---
with tab_edit:
    st.title("📂 Gerenciar Minha Carteira")
    df_edit = st.data_editor(st.session_state.df_carteira, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Aplicar Alterações"):
        st.session_state.df_carteira = df_edit
        st.success("Dados salvos no Dashboard!")
        
