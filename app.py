import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InvestSim Pro v4.0", layout="wide", page_icon="📈")

# --- FUNÇÕES COM CACHE (Para não travar) ---
@st.cache_data(ttl=3600)
def buscar_dados_sp500():
    # Busca a lista oficial das 500 maiores empresas na Wikipedia
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    df = pd.read_html(url)[0]
    return df[['Symbol', 'Security', 'GICS Sector']]

@st.cache_data(ttl=600)
def buscar_precos_lote(tickers):
    if not tickers: return pd.Series()
    # Busca preços de vários ativos de uma só vez
    dados = yf.download(tickers, period="1d", progress=False)
    if 'Close' in dados:
        return dados['Close'].iloc[-1]
    return pd.Series()

# --- MENU LATERAL ---
st.sidebar.title("🚀 InvestSim Pro")
aba = st.sidebar.radio("Navegação", ["Minha Carteira (Planilha)", "Monitor S&P 500 (EUA)"])

# --- ABA 1: MINHA CARTEIRA (CONECTADA AO SEU GOOGLE SHEETS) ---
if aba == "Minha Carteira (Planilha)":
    st.title("📂 Minha Carteira Pessoal")
    st.info("Dados sincronizados com sua planilha Google.")

    try:
        # Conecta usando o link que você salvou nos Secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_pessoal = conn.read().dropna(subset=['Ativo'])
        
        if not df_pessoal.empty:
            # Botão para processar os dados
            if st.button("📊 Atualizar Patrimônio e Lucro"):
                with st.spinner("Buscando cotações atuais..."):
                    tickers = df_pessoal['Ativo'].unique().tolist()
                    precos_mercado = buscar_precos_lote(tickers)
                    
                    # Cálculos Matemáticos
                    df_pessoal['Preço Atual'] = df_pessoal['Ativo'].map(precos_mercado)
                    df_pessoal['Total Investido'] = df_pessoal['Qtd'] * df_pessoal['Preço Médio']
                    df_pessoal['Valor de Mercado'] = df_pessoal['Qtd'] * df_pessoal['Preço Atual']
                    df_pessoal['Lucro/Prejuízo'] = df_pessoal['Valor de Mercado'] - df_pessoal['Total Investido']
                    
                    # Métricas de Topo
                    total_patrimonio = df_pessoal['Valor de Mercado'].sum()
                    lucro_total = df_pessoal['Lucro/Prejuízo'].sum()
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Patrimônio Total", f"R$ {total_patrimonio:,.2f}")
                    c2.metric("Lucro/Prejuízo Geral", f"R$ {lucro_total:,.2f}", 
                              f"{((total_patrimonio/df_pessoal['Total Investido'].sum())-1)*100:.2f}%")
                    
                    # Gráfico de Alocação
                    st.subheader("Distribuição da Carteira")
                    fig = px.pie(df_pessoal, values='Valor de Mercado', names='Ativo', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabela Detalhada
                    st.subheader("Detalhamento")
                    st.dataframe(df_pessoal.style.format({
                        'Preço Médio': 'R$ {:.2f}', 'Preço Atual': 'R$ {:.2f}',
                        'Total Investido': 'R$ {:.2f}', 'Valor de Mercado': 'R$ {:.2f}',
                        'Lucro/Prejuízo': 'R$ {:.2f}'
                    }), use_container_width=True)
        else:
            st.warning("A planilha parece estar vazia.")
            
    except Exception as e:
        st.error(f"Erro de Conexão: Verifique os Secrets e as permissões da planilha.")

# --- ABA 2: MONITOR S&P 500 (AUTOMÁTICO - SEM PLANILHA) ---
elif aba == "Monitor S&P 500 (EUA)":
    st.title("🇺🇸 Monitor S&P 500 (Ranking Automático)")
    st.write("As 500 maiores empresas do mundo atualizadas em tempo real.")

    if st.button("🚀 Carregar Dados do Mercado Americano"):
        with st.spinner("Acessando Wall Street..."):
            df_sp = buscar_dados_sp500()
            # Mostra apenas as 100 primeiras para manter o app rápido
            tickers_sp = df_sp['Symbol'].head(100).tolist() 
            precos_sp = buscar_precos_lote(tickers_sp)
            
            df_sp['Preço (USD)'] = df_sp['Symbol'].map(precos_sp)
            
            # Gráfico das Top 10
            st.subheader("Top 10 Empresas por Valor de Cota")
            st.bar_chart(df_sp.dropna().set_index('Security')['Preço (USD)'].head(10))
            
            # Tabela Completa
            st.subheader("Ranking Geral")
            st.dataframe(df_sp, use_container_width=True)
            
