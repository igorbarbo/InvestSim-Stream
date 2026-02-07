import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InvestSim Pro v3.1", layout="wide", page_icon="💎")

st.title("💎 Gestão de Carteira Inteligente")

def carregar_dados():
    try:
        url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        if 'Ativo' in df.columns:
            df = df.dropna(subset=['Ativo'])
        return df
    except Exception as e:
        st.error(f"Erro na planilha: {e}")
        return pd.DataFrame()

df_pessoal = carregar_dados()

if not df_pessoal.empty:
    if st.button("🚀 Sincronizar e Analisar Mercado"):
        with st.spinner("Buscando cotações e conversão de câmbio..."):
            try:
                # 1. Buscar Dólar (Garantindo valor numérico)
                dados_dolar = yf.download("USDBRL=X", period="1d", progress=False)['Close']
                cotacao_dolar = float(dados_dolar.iloc[-1])
            except:
                cotacao_dolar = 5.00
                st.warning("Usando dólar padrão (R$ 5,00).")

            # 2. Buscar Ativos
            tickers = df_pessoal['Ativo'].unique().tolist()
            dados_mercado = yf.download(tickers, period="1d", progress=False)['Close']
            
            # 3. Processamento de Preços (Tratando Series/Dataframe)
            precos_dict = {}
            for ticker in tickers:
                try:
                    # Garante que pegamos o último preço como um float puro
                    valor = dados_mercado[ticker].iloc[-1] if len(tickers) > 1 else dados_mercado.iloc[-1]
                    precos_dict[ticker] = float(valor)
                except:
                    precos_dict[ticker] = 0.0

            # 4. Cálculos
            df_pessoal['QTD'] = pd.to_numeric(df_pessoal['QTD'], errors='coerce').fillna(0)
            df_pessoal['Preço Médio'] = pd.to_numeric(df_pessoal['Preço Médio'], errors='coerce').fillna(0)
            
            def converter_preco(ativo):
                preco = precos_dict.get(ativo, 0)
                # Se não for brasileiro (.SA), converte
                if not ativo.endswith(".SA"):
                    return preco * cotacao_dolar
                return preco

            df_pessoal['Preço BRL'] = df_pessoal['Ativo'].apply(converter_preco)
            df_pessoal['Investido'] = df_pessoal['QTD'] * df_pessoal['Preço Médio']
            df_pessoal['Atual'] = df_pessoal['QTD'] * df_pessoal['Preço BRL']
            df_pessoal['Lucro R$'] = df_pessoal['Atual'] - df_pessoal['Investido']
            
            # --- MÉTRICAS (Convertendo para float puro para o Streamlit) ---
            total_investido = float(df_pessoal['Investido'].sum())
            total_atual = float(df_pessoal['Atual'].sum())
            lucro_total = total_atual - total_investido
            lucro_perc = (lucro_total / total_investido * 100) if total_investido > 0 else 0

            # Dashboard de Métricas
            c1, c2, c3 = st.columns(3)
            c1.metric("Patrimônio Total", f"R$ {total_atual:,.2f}", f"{lucro_perc:.2f}%")
            c2.metric("Total Investido", f"R$ {total_investido:,.2f}")
            c3.metric("Lucro Líquido", f"R$ {lucro_total:,.2f}")

            # Gráficos
            col_esq, col_dir = st.columns(2)
            with col_esq:
                st.plotly_chart(px.pie(df_pessoal, values='Atual', names='Ativo', hole=0.5, title="Alocação"), use_container_width=True)
            with col_dir:
                st.plotly_chart(px.bar(df_pessoal, x='Ativo', y='Lucro R$', color='Lucro R$', 
                                      color_continuous_scale='RdYlGn', title="Lucro por Ativo"), use_container_width=True)

            st.dataframe(df_pessoal.style.format({
                'Preço Médio': 'R$ {:.2f}', 'Preço BRL': 'R$ {:.2f}', 
                'Investido': 'R$ {:.2f}', 'Atual': 'R$ {:.2f}', 'Lucro R$': 'R$ {:.2f}'
            }))

else:
    st.info("Aguardando sincronização...")
    
