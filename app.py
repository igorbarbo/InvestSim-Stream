import streamlit as st
import pandas as pd
import yfinance as yf
import gc
from Modules import db, pdf_report 
import plotly.express as px

# --- SETUP INICIAL ---
st.set_page_config(page_title="Igorbarbo V6 Pro", layout="wide")
db.init_db()

# Estilização de Luxo (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: white; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    .stTable { background-color: rgba(255,255,255,0.05); border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'serif'; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ---
def run_simulation(df, aporte):
    total_futuro = df['Patrimônio'].sum() + aporte
    objetivo_cada = total_futuro / len(df)
    sugestoes = []
    for _, row in df.iterrows():
        falta = objetivo_cada - row['Patrimônio']
        if falta > 0:
            sugestoes.append({"Ticker": row['ticker'], "Sugerido (R$)": f"R$ {falta:,.2f}"})
    return pd.DataFrame(sugestoes)

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("MENU PRIVATE", ["🏠 Dashboard", "🎯 Simulador de Aporte", "⚙️ Gestão de Ativos", "📄 Relatório PDF"])
df_db = db.get_assets()

# --- MOTOR DE PREÇOS GLOBAL ---
if not df_db.empty:
    try:
        tickers = [f"{t}.SA" for t in df_db['ticker']]
        prices_data = yf.download(tickers, period="1d", progress=False)['Close']
        
        if len(tickers) == 1:
            df_db['Preço'] = prices_data.iloc[-1]
        else:
            last_prices = prices_data.iloc[-1]
            df_db['Preço'] = df_db['ticker'].apply(lambda x: last_prices.get(f"{x}.SA", 0))
        
        df_db['Patrimônio'] = df_db['qtd'] * df_db['Preço']
    except Exception as e:
        st.sidebar.warning("⚠️ Modo Offline: Falha na cotação B3")

# --- INTERFACE ---
if menu == "🏠 Dashboard":
    st.title("💎 Wealth Management Dashboard")
    if not df_db.empty:
        total_brl = df_db['Patrimônio'].sum()
        st.metric("Patrimônio Líquido Estimado", f"R$ {total_brl:,.2f}")
        
        # DEFINIÇÃO DAS CORES MANUAIS (GOLD PALETTE)
        gold_colors = ["#D4AF37", "#C5A028", "#B8860B", "#8B6508", "#FFD700", "#DAA520"]
        
        fig = px.pie(
            df_db, 
            values='Patrimônio', 
            names='ticker', 
            hole=0.6,
            color_discrete_sequence=gold_colors # Cores fixas sem erro
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            margin=dict(t=0, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig, width='stretch')
        gc.collect()
    else:
        st.info("Aguardando inserção de ativos na aba 'Gestão'.")

elif menu == "🎯 Simulador de Aporte":
    st.title("🎯 Estrategista de Capital")
    valor = st.number_input("Capital para Aporte (R$)", min_value=0.0, step=100.0)
    if valor > 0 and not df_db.empty:
        st.table(run_simulation(df_db, valor))

elif menu == "⚙️ Gestão de Ativos":
    st.subheader("🛠️ Custódia de Ativos")
    with st.form("add_form", clear_on_submit=True):
        t = st.text_input("Ticker (ex: BBAS3)").upper().strip()
        q = st.number_input("Quantidade", min_value=0.0)
        p = st.number_input("Preço Médio", min_value=0.0)
        if st.form_submit_button("Confirmar Registro"):
            if t:
                db.add_asset(t, q, p)
                st.success(f"Ativo {t} sincronizado com sucesso!")
                st.rerun()

elif menu == "📄 Relatório PDF":
    st.title("📄 Relatórios Institucionais")
    if not df_db.empty:
        if st.button("Gerar Report de Performance"):
            total = df_db['Patrimônio'].sum()
            pdf_bytes = pdf_report.generate(df_db, total, 0)
            st.download_button("📩 Download PDF Private", data=pdf_bytes, file_name="Report_Private.pdf")
            
