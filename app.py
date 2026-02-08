import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InvestSim Pro v4.0", layout="wide", page_icon="💎")

# --- FUNÇÃO DE DADOS ---
def carregar_dados():
    # Substitua pelo seu link real do Google Sheets (CSV)
    url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df.dropna(subset=['Ativo'])
    except:
        return pd.DataFrame(columns=['Ativo', 'QTD', 'Preço Médio'])

# Inicializa o estado da carteira no navegador
if 'df_carteira' not in st.session_state:
    st.session_state.df_carteira = carregar_dados()

# --- NAVEGAÇÃO POR ABAS ---
aba1, aba2 = st.tabs(["📊 Dashboard e Aportes", "📂 Editar Minha Carteira"])

# --- ABA 1: DASHBOARD E INTELIGÊNCIA ---
with aba1:
    st.title("💎 Gestão de Carteira Inteligente")
    
    # Configurações de Aporte na lateral
    valor_aporte = st.sidebar.number_input("Aporte Mensal (R$)", value=3000.0)
    taxa_mensal = 0.008 # 0,8%

    if st.button("🚀 Sincronizar e Calcular"):
        with st.spinner("Buscando cotações e calculando lucro..."):
            df_calc = st.session_state.df_carteira.copy()
            
            # Busca cotações e dólar
            cotacao_dolar = float(yf.download("USDBRL=X", period="1d", progress=False)['Close'].iloc[-1])
            tickers = df_calc['Ativo'].unique().tolist()
            dados_mercado = yf.download(tickers, period="1d", progress=False)['Close']
            precos_dict = {t: float(dados_mercado[t].iloc[-1] if len(tickers) > 1 else dados_mercado.iloc[-1]) for t in tickers}

            # Cálculos de Patrimônio e Lucro
            df_calc['Preço BRL'] = df_calc['Ativo'].apply(lambda x: precos_dict.get(x, 0) * (cotacao_dolar if not x.endswith(".SA") else 1))
            df_calc['Total Atual'] = df_calc['QTD'] * df_calc['Preço BRL']
            df_calc['Investido'] = df_calc['QTD'] * df_calc['Preço Médio']
            df_calc['Lucro R$'] = df_calc['Total Atual'] - df_calc['Investido']
            
            total_patrimonio = df_calc['Total Atual'].sum()
            lucro_mensal = total_patrimonio * taxa_mensal

            # Cards de Resumo
            c1, c2, c3 = st.columns(3)
            c1.metric("Patrimônio Total", f"R$ {total_patrimonio:,.2f}")
            c2.metric("Lucro Estimado/Mês", f"R$ {lucro_mensal:,.2f}")
            c3.metric("Dólar hoje", f"R$ {cotacao_dolar:,.2f}")

            # Gráficos
            col_esq, col_dir = st.columns(2)
            with col_esq:
                st.plotly_chart(px.pie(df_calc, values='Total Atual', names='Ativo', hole=0.5, title="Divisão da Carteira"), use_container_width=True)
            with col_dir:
                st.plotly_chart(px.bar(df_calc, x='Ativo', y='Lucro R$', color='Lucro R$', color_continuous_scale='RdYlGn', title="Lucro por Ativo"), use_container_width=True)

            st.success(f"Dica: Para manter 0,8% ao mês, seu próximo aporte deve ser de R$ {valor_aporte:,.2f}")

# --- ABA 2: EDITOR DE DADOS ---
with aba2:
    st.title("📂 Gerenciar Ativos")
    st.write("Edite os valores abaixo. Lembre-se: mudanças aqui são temporárias até que você salve na sua planilha oficial.")
    
    # O Editor de Dados
    df_editado = st.data_editor(
        st.session_state.df_carteira,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_real"
    )

    if st.button("💾 Aplicar Mudanças no Dashboard"):
        st.session_state.df_carteira = df_editado
        st.success("Dados atualizados! Volte na aba do Dashboard e clique em Sincronizar.")
        
