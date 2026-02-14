import plotly.express as px
import pandas as pd
import io
import yfinance as yf

def gerar_grafico_setor(df):
    return px.pie(df, values='Patrimônio', names='setor', hole=0.4, title="Divisão por Setor")

def calcular_risco_retorno(tickers):
    if not tickers: return None
    dados = yf.download([f"{t}.SA" for t in tickers], period="1y")['Adj Close']
    ret = dados.pct_change().dropna()
    return ret.mean()*252, ret.std()*(252**0.5), ret.corr()

def exportar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()
    
