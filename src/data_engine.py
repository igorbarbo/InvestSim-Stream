import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=600)
def fetch_data():
    # Esta é a função que estava faltando no seu arquivo!
    url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df.dropna(subset=['Ativo'])
    except Exception as e:
        st.error(f"Erro ao ler Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)
def sync_prices(df):
    try:
        tickers = df['Ativo'].unique().tolist()
        data = yf.download(tickers, period="1d", progress=False)['Close']
        
        p_dict = {}
        for t in tickers:
            # Tratamento para um ou vários ativos
            if len(tickers) > 1:
                val = data[t].iloc[-1]
            else:
                val = data.iloc[-1]
            p_dict[t] = float(val)
            
        df['Preço Atual'] = df['Ativo'].map(p_dict)
        df['Patrimônio'] = df['QTD'] * df['Preço Atual']
        df['Valorização %'] = (df['Preço Atual'] / df['Preço Médio'] - 1) * 100
        return df
    except Exception as e:
        st.warning(f"Erro na Bolsa: {e}")
        return df
        
