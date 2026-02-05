import yfinance as yf
import pandas as pd

def get_price_history(ticker, period="5y"):
    """Busca histórico de preços de um ativo."""
    try:
        # Se o ticker não tiver .SA e for brasileiro, yfinance pode falhar
        # Mas vamos manter simples para o teste
        data = yf.download(ticker, period=period)
        if data.empty:
            return None
        return data["Adj Close"]
    except Exception as e:
        return None
        
