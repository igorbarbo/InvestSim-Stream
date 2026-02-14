# services/teto_service.py
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Tuple
from config.settings import settings
from services.preco_service import session

class PrecoTetoService:
    """Serviço para cálculo de preço teto pelo método Bazin."""
    
    @staticmethod
    def calcular_bazin(ticker: str, dy_desejado: float = 0.06) -> Tuple[Optional[float], str]:
        """
        Calcula preço teto baseado na soma dos dividendos dos últimos 12 meses.
        Retorna (preco_teto, mensagem).
        """
        try:
            # Formatar ticker
            if ticker[-1].isdigit() and len(ticker) >= 5:
                ticker_yf = f"{ticker}.SA"
            else:
                ticker_yf = ticker
            
            acao = yf.Ticker(ticker_yf, session=session)
            dividends = acao.dividends
            
            if dividends.empty:
                return None, "Sem histórico de dividendos"
            
            # Últimos 12 meses
            um_ano_atras = datetime.now() - timedelta(days=365)
            dividends_12m = dividends[dividends.index >= um_ano_atras].sum()
            
            if dividends_12m <= 0:
                # Tenta usar os últimos 4 trimestres como fallback
                dividends_12m = dividends.tail(4).sum()
            
            if dividends_12m <= 0:
                return None, "Sem dividendos nos últimos 12 meses"
            
            preco_teto = dividends_12m / dy_desejado
            return preco_teto, f"R$ {preco_teto:.2f}"
        
        except Exception as e:
            return None, str(e)
