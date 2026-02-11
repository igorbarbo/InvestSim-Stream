import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import numpy as np

# --- 1. CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Terminal Igorbarbo", layout="wide", page_icon="📈")

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
        #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE LOGIN ---
if 'logado' not in st.session_state: 
    st.session_state.logado = False

SENHA_MESTRA = "igor123"

if not st.session_state.logado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.title("🛡️ Terminal Igorbarbo")
        senha_input = st.text_input("Senha Mestre:", type="password")
        if st.button("DESBLOQUEAR ACESSO"):
            if senha_input == SENHA_MESTRA:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    st.stop()

# --- 3. CARREGAMENTO DE DADOS (PLANILHA GOOGLE) ---
@st.cache_data(ttl=600)
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df.dropna(subset=['Ativo'])
    except:
        return pd.DataFrame(columns=['Ativo', 'QTD', 'Preço Médio'])

if 'df_carteira' not in st.session_state:
    st.session_state.df_carteira = carregar_dados()

# --- 4. NAVEGAÇÃO POR ABAS ---
tab_dash, tab_risco, tab_val, tab_proj, tab_edit = st.tabs([
    "📊 DASHBOARD", "⚠️ RISCO", "⚖️ VALUATION", "🚀 BOLA DE NEVE", "📂 GERENCIAR"
])

# --- ABA 1: DASHBOARD REAL ---
with tab_dash:
    st.subheader("💎 Patrimônio Real Atual")
    if st.button("🔄 SINCRONIZAR COM O MERCADO"):
        df = st.session_state.df_carteira.copy()
        tickers = df['Ativo'].unique().tolist()
        with st.spinner("Buscando cotações reais..."):
            dolar = float(yf.download("USDBRL=X", period="1d", progress=False)['Close'].iloc[-1])
            precos = yf.download(tickers, period="1d", progress=False)['Close']
            
            p_dict = {t: float(precos[t].iloc[-1] if len(tickers) > 1 else precos.iloc[-1]) for t in tickers}
            df['Patrimônio'] = df['QTD'] * df['Ativo'].apply(lambda x: p_dict.get(x, 0) * (dolar if not x.endswith(".SA") else 1))
            
            st.metric("PATRIMÔNIO TOTAL", f"R$ {df['Patrimônio'].sum():,.2f}")
            fig_pizza = px.pie(df, values='Patrimônio', names='Ativo', hole=0.5, template="plotly_dark")
            st.plotly_chart(fig_pizza, use_container_width=True)

# --- ABA 2: ANÁLISE DE RISCO ---
with tab_risco:
    st.subheader("⚠️ Análise de Concentração")
    df_risco = st.session_state.df_carteira.copy()
    if not df_risco.empty:
        fig_bar = px.bar(df_risco, x='Ativo', y='QTD', title="Quantidade por Ativo", template="plotly_dark")
        fig_bar.update_traces(marker_color='#00a3ff')
        st.plotly_chart(fig_bar, use_container_width=True)
        st.info("💡 Lembre-se: Diversificar é o único 'almoço grátis' no mercado financeiro.")

# --- ABA 3: VALUATION ---
with tab_val:
    st.subheader("⚖️ Avaliação de Preço Justo")
    st.write("Baseado no seu Preço Médio cadastrado na planilha.")
    st.dataframe(st.session_state.df_carteira[['Ativo', 'Preço Médio']], use_container_width=True)

# --- ABA 4: PROJEÇÃO BOLA DE NEVE (O SEU PEDIDO) ---
with tab_proj:
    st.title("🚀 Simulador de Futuro")
    st.write("Veja quanto você terá de investir e quanto os juros vão render.")
    
    c_in1, c_in2 = st.columns(2)
    with c_in1:
        v_aporte = st.number_input("Aporte Mensal (R$):", value=3000, step=100)
        v_anos = st.slider("Prazo da Projeção (Anos):", 1, 40, 10)
    with c_in2:
        v_taxa = st.slider("Taxa de Juros Anual Esperada (%):", 1.0, 20.0, 10.0)
        v_ir = st.selectbox("Imposto de Renda sobre Lucro (%):", [15, 17.5, 20, 22.5], index=0)

    # Lógica de Cálculo Mês a Mês
    meses = v_anos * 12
    r_mensal = (1 + v_taxa/100)**(1/12) - 1
    
    dados_proj = []
    saldo_acumulado = 0
    investido_bolso = 0
    
    for m in range(1, meses + 1):
        juros_mes = saldo_acumulado * r_mensal
        investido_bolso += v_aporte
        saldo_acumulado = saldo_acumulado + v_aporte + juros_mes
        
        dados_proj.append({
            "Mês": m,
            "Total Investido (Bolso)": investido_bolso,
            "Juros do Mês (Bola de Neve)": juros_mes,
            "Patrimônio Bruto": saldo_acumulado
        })

    df_final = pd.DataFrame(dados_proj)
    
    # Métricas Finais
    bruto_final = df_final["Patrimônio Bruto"].iloc[-1]
    total_do_bolso = df_final["Total Investido (Bolso)"].iloc[-1]
    lucro_total = bruto_final - total_do_bolso
    ir_pagar = lucro_total * (v_ir / 100)
    liquido_final = bruto_final - ir_pagar

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("INVESTIDO DO BOLSO", f"R$ {total_do_bolso:,.2f}")
    m2.metric("LUCRO (SÓ JUROS)", f"R$ {lucro_total:,.2f}")
    m3.metric("LÍQUIDO (PÓS IMPOSTO)", f"R$ {liquido_final:,.2f}")

    # Gráfico de Crescimento
    st.plotly_chart(px.area(df_final, x="Mês", y="Patrimônio Bruto", title="Crescimento do Patrimônio", template="plotly_dark").update_traces(line_color='#00ff88'), use_container_width=True)

    # TABELA MÊS A MÊS
    st.subheader("📋 Tabela de Evolução Mensal")
    df_formatado = df_final.copy()
    for c in ["Total Investido (Bolso)", "Juros do Mês (Bola de Neve)", "Patrimônio Bruto"]:
        df_formatado[c] = df_formatado[c].map("R$ {:,.2f}".format)
    st.dataframe(df_formatado, use_container_width=True)

# --- ABA 5: GERENCIAR ---
with tab_edit:
    st.subheader("📂 Gerenciar Dados da Planilha")
    st.data_editor(st.session_state.df_carteira, use_container_width=True)
    if st.button("🚪 LOGOFF"):
        st.session_state.logado = False
        st.rerun()
        
