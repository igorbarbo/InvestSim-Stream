import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from urllib.request import Request, urlopen

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InvestSim Pro v4.0", layout="wide", page_icon="📈")

# --- FUNÇÕES COM CACHE ---
@st.cache_data(ttl=86400)
def buscar_dados_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        # Adiciona User-Agent para evitar erro urllib.error.HTTPError
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as response:
            df = pd.read_html(response)[0]
        return df[['Symbol', 'Security', 'GICS Sector']]
    except Exception as e:
        st.error(f"Erro ao acessar a lista do S&P 500: {e}")
        return pd.DataFrame(columns=['Symbol', 'Security', 'GICS Sector'])

@st.cache_data(ttl=600)
def buscar_precos_lote(tickers):
    if not tickers: return pd.Series()
    try:
        # Download em lote para performance
        dados = yf.download(tickers, period="1d", progress=False)
        if not dados.empty:
            if 'Close' in dados:
                fechamento = dados['Close']
                # Trata se o retorno for apenas um ticker (Series) ou vários (DataFrame)
                if isinstance(fechamento, pd.Series):
                    return fechamento
                return fechamento.iloc[-1]
    except Exception as e:
        st.sidebar.error(f"Erro ao buscar preços: {e}")
    return pd.Series()

# --- MENU LATERAL ---
st.sidebar.title("🚀 InvestSim Pro")
aba = st.sidebar.radio("Navegação", ["Minha Carteira (Planilha)", "Monitor S&P 500 (EUA)"])

# --- ABA 1: MINHA CARTEIRA ---
if aba == "Minha Carteira (Planilha)":
    st.title("📂 Minha Carteira Pessoal")
    
    try:
        # Conexão com Google Sheets via Secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_pessoal = conn.read().dropna(subset=['Ativo'])
        
        if not df_pessoal.empty:
            if st.button("📊 Atualizar Patrimônio e Lucro"):
                with st.spinner("Buscando cotações atuais (Yahoo Finance)..."):
                    tickers = df_pessoal['Ativo'].unique().tolist()
                    precos_mercado = buscar_precos_lote(tickers)
                    
                    # Cálculos Financeiros
                    df_pessoal['Preço Atual'] = df_pessoal['Ativo'].map(precos_mercado)
                    df_pessoal['Total Investido'] = df_pessoal['Qtd'] * df_pessoal['Preço Médio']
                    df_pessoal['Valor de Mercado'] = df_pessoal['Qtd'] * df_pessoal['Preço Atual']
                    df_pessoal['Lucro/Prejuízo'] = df_pessoal['Valor de Mercado'] - df_pessoal['Total Investido']
                    
                    # Métricas de Resumo
                    total_patrimonio = df_pessoal['Valor de Mercado'].sum()
                    investimento_total = df_pessoal['Total Investido'].sum()
                    lucro_total = df_pessoal['Lucro/Prejuízo'].sum()
                    rentabilidade = ((total_patrimonio / investimento_total) - 1) * 100 if investimento_total > 0 else 0
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Patrimônio Total", f"R$ {total_patrimonio:,.2f}")
                    c2.metric("Lucro/Prejuízo Geral", f"R$ {lucro_total:,.2f}", f"{rentabilidade:.2f}%")
                    
                    # Visualização Gráfica
                    st.subheader("Distribuição da Carteira")
                    fig = px.pie(df_pessoal, values='Valor de Mercado', names='Ativo', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabela Formatada
                    st.dataframe(df_pessoal.style.format({
                        'Preço Médio': 'R$ {:.2f}', 'Preço Atual': 'R$ {:.2f}',
                        'Total Investido': 'R$ {:.2f}', 'Valor de Mercado': 'R$ {:.2f}',
                        'Lucro/Prejuízo': 'R$ {:.2f}'
                    }), use_container_width=True)
        else:
            st.warning("Preencha sua planilha Google Sheets com os ativos.")
    except Exception as e:
        st.error("Erro de conexão. Verifique se o link da planilha nos Secrets está correto.")

# --- ABA 2: MONITOR S&P 500 ---
elif aba == "Monitor S&P 500 (EUA)":
    st.title("🇺🇸 Monitor S&P 500")
    st.write("Acesso automático às 500 maiores empresas americanas via Wikipedia.")
    
    if st.button("🚀 Carregar Ranking Atualizado"):
        with st.spinner("Acessando dados do mercado..."):
            df_sp = buscar_dados_sp500()
            if not df_sp.empty:
                st.success(f"Sucesso! {len(df_sp)} empresas encontradas.")
                st.dataframe(df_sp, use_container_width=True)
                
