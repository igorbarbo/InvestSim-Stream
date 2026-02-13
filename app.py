import streamlit as st
import pandas as pd
import yfinance as yf
import gc
import time
from Modules import db, pdf_report 
import plotly.express as px
from alpha_vantage.timeseries import TimeSeries

# --- CONFIGURAÇÃO E LOGIN ---
st.set_page_config(page_title="Igorbarbo V8 Ultimate", layout="wide")
db.init_db()

def check_password():
    """Retorna True se o usuário inseriu a senha correta."""
    def password_entered():
        if st.session_state["password"] == "1234": # Altere sua senha aqui
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🏛️ Acesso Restrito - Private Banking")
        st.text_input("Senha de Acesso", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Senha de Acesso", type="password", on_change=password_entered, key="password")
        st.error("⚠️ Senha incorreta.")
        return False
    else:
        return True

if check_password():
    # Estilização Luxury
    st.markdown("""
        <style>
        .stApp { background-color: #05070A; color: white; }
        [data-testid="stMetricValue"] { color: #D4AF37 !important; }
        .stProgress > div > div > div > div { background-color: #D4AF37 !important; }
        h1, h2, h3 { color: #D4AF37 !important; font-family: 'serif'; }
        </style>
        """, unsafe_allow_html=True)

    # Chave Alpha Vantage segura via Secrets
    AV_API_KEY = st.secrets.get("AV_API_KEY", "DWWXZRRXKRHYCBGP")

    @st.cache_data(ttl=3600)
    def get_av_price(ticker):
        try:
            ts = TimeSeries(key=AV_API_KEY, output_format='pandas')
            data, _ = ts.get_quote_endpoint(symbol=f"{ticker}.SAO")
            return float(data['05. price'].iloc[0])
        except: return 0.0

    # --- NAVEGAÇÃO ---
    st.sidebar.title("💎 IGORBARBO V8")
    menu = st.sidebar.radio("MENU", ["🏠 Dashboard", "💡 Sugestão", "🎯 Projeção", "⚙️ Gestão", "📄 PDF"])
    df_db = db.get_assets()

    # --- ATUALIZAÇÃO DE PREÇOS ---
    if not df_db.empty:
        try:
            tickers_yf = [f"{t}.SA" for t in df_db['ticker']]
            prices = yf.download(tickers_yf, period="1d", progress=False)['Close']
            if len(tickers_yf) == 1:
                df_db['Preço'] = prices.iloc[-1]
            else:
                last_p = prices.iloc[-1]
                df_db['Preço'] = df_db['ticker'].apply(lambda x: last_p.get(f"{x}.SA", 0))
        except:
            df_db['Preço'] = df_db['ticker'].apply(get_av_price)
        
        df_db['Patrimônio'] = df_db['qtd'] * df_db['Preço']
        # Setor agora vem do banco de dados ou classificação manual

    # --- TELAS ---
    if menu == "🏠 Dashboard":
        st.title("🏛️ Wealth Portfolio V8")
        if not df_db.empty:
            total = df_db['Patrimônio'].sum()
            renda = total * 0.0085
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Patrimônio Total", f"R$ {total:,.2f}")
            c2.metric("Renda Passiva Mensal", f"R$ {renda:,.2f}")
            c3.metric("Meta R$ 100k", f"{min(total/1000, 100):.1f}%")
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.plotly_chart(px.pie(df_db, values='Patrimônio', names='ticker', hole=0.5, title="Ativos", color_discrete_sequence=px.colors.sequential.Gold), use_container_width=True)
            with col_g2:
                # Na V8, o setor é cadastrado pelo usuário
                st.plotly_chart(px.pie(df_db, values='Patrimônio', names='setor', hole=0.5, title="Diversificação", color_discrete_sequence=["#D4AF37", "#8B6914"]), use_container_width=True)
        else:
            st.info("Sua carteira está vazia. Vá em Gestão.")

    elif menu == "⚙️ Gestão":
        st.title("⚙️ Gerenciar Carteira")
        
        with st.form("add"):
            c_t, c_q, c_p, c_s = st.columns(4)
            t = c_t.text_input("Ticker").upper()
            q = c_q.number_input("Quantidade", min_value=0.0)
            p = c_p.number_input("Preço Médio", min_value=0.0)
            s = c_s.selectbox("Setor", ["FII Papel", "FII Tijolo", "Ações", "ETF", "Renda Fixa", "BDR"])
            if st.form_submit_button("Adicionar Ativo"):
                db.add_asset(t, q, p, s) # Certifique-se que db.add_asset aceita o campo setor
                st.rerun()

        st.write("---")
        if not df_db.empty:
            for idx, row in df_db.iterrows():
                col_at, col_btn = st.columns([4, 1])
                col_at.write(f"**{row['ticker']}** - {row['qtd']} cotas (Setor: {row['setor']})")
                if col_btn.button(f"Excluir {row['ticker']}", key=f"del_{row['ticker']}"):
                    db.delete_asset(row['ticker']) # Certifique-se que db.delete_asset existe
                    st.rerun()

    elif menu == "🎯 Projeção":
        st.title("🚀 Simulador de Futuro")
        aporte = st.number_input("Aporte Mensal", value=150)
        anos = st.slider("Anos", 1, 30, 10)
        taxa = 0.0085
        df_p = pd.DataFrame({'Mes': range(1, (anos*12)+1)})
        df_p['Com Reinvestimento'] = [aporte * (((1+taxa)**m - 1)/taxa) for m in df_p['Mes']]
        df_p['Sem Reinvestimento'] = [aporte * m for m in df_p['Mes']]
        st.plotly_chart(px.line(df_p, x='Mes', y=['Com Reinvestimento', 'Sem Reinvestimento'], color_discrete_map={'Com Reinvestimento': '#D4AF37', 'Sem Reinvestimento': '#FF4B4B'}))
        st.error(f"Perda por gastar dividendos: R$ {df_p['Com Reinvestimento'].iloc[-1] - df_p['Sem Reinvestimento'].iloc[-1]:,.2f}")

    elif menu == "📄 PDF":
        if not df_db.empty and st.button("Gerar PDF"):
            pdf_bytes = pdf_report.generate(df_db, df_db['Patrimônio'].sum(), 0)
            st.download_button("Baixar Relatório", pdf_bytes, "Invest_Report.pdf")

    gc.collect()
    
