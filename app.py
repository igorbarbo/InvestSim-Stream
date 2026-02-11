import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import numpy as np

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Terminal Igorbarbo Expert", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
        .stApp { background-color: #05070a; color: #e0e0e0; }
        [data-testid="stMetric"] { 
            background-color: #11151c; 
            padding: 15px; border-radius: 15px; border: 1px solid #1a202c; 
        }
        [data-testid="stMetricValue"] { color: #00ff88 !important; }
        .stButton>button {
            width: 100%; border-radius: 12px; height: 3.5em;
            background-image: linear-gradient(to right, #00ff88, #00a3ff);
            color: #05070a; font-weight: bold; border: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIN ---
if 'logado' not in st.session_state: st.session_state.logado = False
SENHA_MESTRA = "igor123"

if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.title("🛡️ Acesso Restrito")
        senha = st.text_input("Senha Mestre:", type="password")
        if st.button("DESBLOQUEAR TERMINAL"):
            if senha == SENHA_MESTRA:
                st.session_state.logado = True
                st.rerun()
    st.stop()

# --- 3. DADOS ---
@st.cache_data(ttl=600)
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df.dropna(subset=['Ativo'])
    except: return pd.DataFrame(columns=['Ativo', 'QTD', 'Preço Médio'])

if 'df_carteira' not in st.session_state: st.session_state.df_carteira = carregar_dados()

# --- 4. ABAS ---
tab_dash, tab_radar, tab_proj, tab_edit = st.tabs(["📊 DASHBOARD", "🎯 RADAR DE COMPRA", "🚀 BOLA DE NEVE", "📂 GERENCIAR"])

with tab_dash:
    st.subheader("💎 Patrimônio em Tempo Real")
    if st.button("🔄 ATUALIZAR COTAÇÕES"):
        df = st.session_state.df_carteira.copy()
        tickers = df['Ativo'].unique().tolist()
        with st.spinner("Sincronizando com a Bolsa..."):
            dolar = float(yf.download("USDBRL=X", period="1d", progress=False)['Close'].iloc[-1])
            precos = yf.download(tickers, period="1d", progress=False)['Close']
            p_dict = {t: float(precos[t].iloc[-1] if len(tickers) > 1 else precos.iloc[-1]) for t in tickers}
            df['Preço Atual'] = df['Ativo'].map(p_dict)
            df['Patrimônio'] = df['QTD'] * df['Preço Atual'] * df['Ativo'].apply(lambda x: dolar if not x.endswith(".SA") else 1)
            st.metric("TOTAL INVESTIDO", f"R$ {df['Patrimônio'].sum():,.2f}")
            st.plotly_chart(px.pie(df, values='Patrimônio', names='Ativo', hole=0.5, template="plotly_dark"), use_container_width=True)

with tab_radar:
    st.subheader("🎯 Radar de Oportunidades")
    st.write("Comparação entre o seu Preço Médio e o Valor de Mercado atual.")
    
    df_radar = st.session_state.df_carteira.copy()
    tickers = df_radar['Ativo'].unique().tolist()
    precos = yf.download(tickers, period="1d", progress=False)['Close']
    p_dict = {t: float(precos[t].iloc[-1] if len(tickers) > 1 else precos.iloc[-1]) for t in tickers}
    
    df_radar['Preço Atual'] = df_radar['Ativo'].map(p_dict)
    df_radar['Status'] = np.where(df_radar['Preço Atual'] < df_radar['Preço Médio'], "🟢 OPORTUNIDADE", "🔴 ACIMA DO PM")
    df_radar['Desconto %'] = ((df_radar['Preço Atual'] / df_radar['Preço Médio']) - 1) * 100
    
    st.dataframe(df_radar[['Ativo', 'Preço Médio', 'Preço Atual', 'Status', 'Desconto %']].style.format({'Desconto %': '{:.2f}%'}), use_container_width=True)
    st.info("💡 Ações com 'OPORTUNIDADE' estão custando menos do que você pagou na média. Pode ser hora de baixar seu PM!")

with tab_proj:
    st.title("🚀 Projeção Nível Expert")
    col1, col2 = st.columns(2)
    with col1:
        v_aporte = st.number_input("Aporte Mensal (R$):", value=3000)
        v_anos = st.slider("Tempo (Anos):", 1, 40, 10)
    with col2:
        v_taxa = st.slider("Rentabilidade Anual (%):", 1.0, 20.0, 10.0)
        v_ir = st.selectbox("Imposto de Renda (%):", [15, 17.5, 20, 22.5], index=0)

    meses = v_anos * 12
    r_mensal = (1 + v_taxa/100)**(1/12) - 1
    
    dados_m = []
    saldo = 0
    virada_mes = None
    
    for m in range(1, meses + 1):
        juros = saldo * r_mensal
        if juros >= v_aporte and virada_mes is None:
            virada_mes = m
        saldo = saldo + v_aporte + juros
        dados_m.append({"Mês": m, "Saldo": saldo, "Juros": juros})
    
    df_p = pd.DataFrame(dados_m)
    
    # Métricas
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("BRUTO FINAL", f"R$ {saldo:,.2f}")
    c2.metric("LUCRO LÍQUIDO", f"R$ {((saldo - (v_aporte*meses)) * (1 - v_ir/100)):,.2f}")
    
    if virada_mes:
        c3.metric("PONTO DE VIRADA", f"Mês {virada_mes}", help="Mês onde os juros superam seu aporte!")
        st.success(f"🎊 No mês **{virada_mes}** (**Ano {virada_mes//12}**), o dinheiro passa a trabalhar mais que você!")
    else:
        c3.metric("PONTO DE VIRADA", "Ainda não atingido")

    st.plotly_chart(px.area(df_p, x="Mês", y="Saldo", title="Crescimento Exponencial", template="plotly_dark"), use_container_width=True)

with tab_edit:
    st.subheader("📂 Gerenciar")
    st.data_editor(st.session_state.df_carteira, use_container_width=True)
    if st.button("SAIR"):
        st.session_state.logado = False
        st.rerun()
    
