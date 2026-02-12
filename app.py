import streamlit as st
import pandas as pd
import yfinance as yf
import google.generativeai as genai
import gc
from Modules import db, pdf_report 
import plotly.express as px

# --- SETUP LUXO & PERFORMANCE ---
st.set_page_config(page_title="Igorbarbo V6 Pro", layout="wide")
db.init_db()

# CSS para Dark Mode Real e Cards Dourados
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: white; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    .stTable { background-color: rgba(255,255,255,0.05); border-radius: 10px; }
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

if menu == "🏠 Dashboard":
    st.title("💎 Wealth Management Dashboard")
    if not df_db.empty:
        with st.spinner("Sincronizando com a B3..."):
            tickers = [f"{t}.SA" for t in df_db['ticker']]
            prices = yf.download(tickers, period="1d", progress=False)['Close']
            
            # Tratamento para um ou vários ativos
            if len(tickers) == 1:
                last_price = prices.iloc[-1]
                df_db['Preço'] = last_price
            else:
                last_prices = prices.iloc[-1]
                df_db['Preço'] = df_db['ticker'].apply(lambda x: last_prices.get(f"{x}.SA", 0))
            
            df_db['Patrimônio'] = df_db['qtd'] * df_db['Preço']
        
        c1, c2 = st.columns(2)
        c1.metric("Patrimônio Total", f"R$ {df_db['Patrimônio'].sum():,.2f}")
        
        # Gráfico atualizado para nova versão do Streamlit
        fig = px.pie(df_db, values='Patrimônio', names='ticker', hole=0.5, 
                     color_discrete_sequence=px.colors.sequential.Gold)
        st.plotly_chart(fig, width='stretch') # Ajuste conforme log
        gc.collect()

elif menu == "🎯 Simulador de Aporte":
    st.title("🎯 Estrategista de Capital")
    valor = st.number_input("Valor disponível para aporte (R$)", min_value=0.0, step=100.0)
    if valor > 0 and not df_db.empty:
        sugestoes = run_simulation(df_db, valor)
        st.table(sugestoes)
        st.info("💡 A IA prioriza ativos que estão abaixo da média de equilíbrio da sua carteira.")

elif menu == "⚙️ Gestão de Ativos":
    st.subheader("🛠️ Cadastro de Ativos")
    with st.form("add_form", clear_on_submit=True):
        t = st.text_input("Ticker (ex: ITUB4)").upper().strip()
        q = st.number_input("Quantidade", min_value=0.0)
        p = st.number_input("Preço Médio", min_value=0.0)
        if st.form_submit_button("Salvar no Banco SQL"):
            if t:
                db.add_asset(t, q, p)
                st.success(f"Ativo {t} salvo com sucesso!")
                st.rerun()

elif menu == "📄 Relatório PDF":
    st.title("📄 Relatório de Elite")
    if not df_db.empty:
        if st.button("Gerar Wealth Report"):
            total = df_db['Patrimônio'].sum() if 'Patrimônio' in df_db else 0
            pdf_bytes = pdf_report.generate(df_db, total, 0)
            st.download_button("📩 Baixar PDF Private", data=pdf_bytes, file_name="Igorbarbo_Report.pdf")
    else:
        st.warning("Adicione ativos para gerar o relatório.")
        
