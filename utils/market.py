import yfinance as yf
import pandas as pd


def get_price_history(ticker: str, period: str = "5y") -> pd.Series | None:
    """
    Busca histórico de preços ajustados (Adj Close) de um ativo.
    Retorna None se não houver dados.
    """

    if not ticker:
        return None

    ticker = ticker.strip().upper()

    try:
        data = yf.download(
            ticker,
            period=period,
            progress=False,
            auto_adjust=False
        )

        if data is None or data.empty:
            return None

        if "Adj Close" not in data.columns:
            return None

        return data["Adj Close"].dropna()

    except Exception:
        return None
