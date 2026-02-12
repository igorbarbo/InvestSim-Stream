import streamlit as st
import pandas as pd
import yfinance as yf
import gc
from Modules import db, pdf_report 
import plotly.express as px

# --- SETUP INICIAL ---
st.set_page_config(page_title="Igorbarbo V6 Pro", layout="wide")
db.init_db()

# Estilização de Luxo
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: white; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    .stTable { background-color: rgba(255,255,255,0.05); border-radius: 10px; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'serif'; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DA ESTRATÉGIA ---
def run_simulation(df, aporte):
    total_patrimonio = df['Patrimônio'].sum()
    total_futuro = total_patrimonio + aporte
    objetivo_cada = total_futuro / len(df)
    
    sugestoes = []
    for _, row in df.iterrows():
        falta = objetivo_cada - row['Patrimônio']
        if falta > 0:
            sugestoes.append({
                "Ativo": row['ticker'], 
                "Quanto Comprar (R$)": f"R$ {falta:,.2f}",
                "Objetivo Final": f"R$ {objetivo_cada:,.2f}"
            })
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
    except:
        st.sidebar.warning("⚠️ Erro de conexão B3.")

# --- RENDERIZAÇÃO DAS TELAS ---
if menu == "🏠 Dashboard":
    st.title("💎 Wealth Dashboard")
    if not df_db.empty:
        st.metric("Patrimônio Total", f"R$ {df_db['Patrimônio'].sum():,.2f}")
        fig = px.pie(df_db, values='Patrimônio', names='ticker', hole=0.6, 
                     color_discrete_sequence=["#D4AF37", "#C5A028", "#B8860B", "#8B6508"])
        st.plotly_chart(fig, use_container_width=True)
        gc.collect()

elif menu == "🎯 Simulador de Aporte":
    st.title("🎯 Estrategista de Capital")
    valor = st.number_input("Capital para Aporte (R$)", min_value=0.0, step=100.0)
    
    if valor > 0:
        if not df_db.empty:
            # GERA A ESTRATÉGIA
            sugestoes_df = run_simulation(df_db, valor)
            
            if not sugestoes_df.empty:
                st.subheader("Sugestão de Rebalanceamento")
                # MOSTRA A TABELA NA TELA
                st.dataframe(sugestoes_df, use_container_width=True)
                st.success("✅ Estratégia gerada com base no equilíbrio da carteira.")
            else:
                st.info("Sua carteira já está equilibrada. O aporte pode ser distribuído igualmente.")
        else:
            st.warning("Adicione ativos na Gestão para simular.")

elif menu == "⚙️ Gestão de Ativos":
    st.subheader("🛠️ Custódia de Ativos")
    with st.form("add_form", clear_on_submit=True):
        t = st.text_input("Ticker (ex: ITUB4)").upper().strip()
        q = st.number_input("Quantidade", min_value=0.0)
        p = st.number_input("Preço Médio", min_value=0.0)
        if st.form_submit_button("Confirmar Registro"):
            if t:
                db.add_asset(t, q, p)
                st.success(f"Ativo {t} salvo!")
                st.rerun()

elif menu == "📄 Relatório PDF":
    st.title("📄 Relatório Institucional")
    if not df_db.empty:
        if st.button("Gerar PDF"):
            pdf_bytes = pdf_report.generate(df_db, df_db['Patrimônio'].sum(), 0)
            st.download_button("📩 Download PDF", data=pdf_bytes, file_name="Report.pdf")
            
