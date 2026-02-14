# services/preco_service.py
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
import streamlit as st
from config.settings import settings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configura sessão HTTP com retry e timeout
session = requests.Session()
retry = Retry(total=2, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

class DadosAtivo:
    """Estrutura de dados retornada pelo serviço de preços."""
    
    def __init__(self, ticker: str, preco_atual: float = 0.0, status: str = "erro",
                 mensagem: str = "", preco_medio_12m: float = 0.0,
                 percentil_20: float = 0.0, percentil_80: float = 0.0,
                 minimo_5y: float = 0.0, maximo_5y: float = 0.0,
                 variacao_anual: float = 0.0, dividend_yield: Optional[float] = None,
                 historico: Optional[pd.DataFrame] = None):
        self.ticker = ticker
        self.preco_atual = preco_atual
        self.status = status
        self.mensagem = mensagem
        self.preco_medio_12m = preco_medio_12m
        self.percentil_20 = percentil_20
        self.percentil_80 = percentil_80
        self.minimo_5y = minimo_5y
        self.maximo_5y = maximo_5y
        self.variacao_anual = variacao_anual
        self.dividend_yield = dividend_yield
        self.historico = historico if historico is not None else pd.DataFrame()


class PrecoService:
    """Serviço otimizado para busca de preços com paralelismo, cache e timeout."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or settings.MAX_WORKERS
        self.timeout = settings.YF_TIMEOUT
    
    def _formatar_ticker(self, ticker: str) -> str:
        """Formata ticker para yfinance (adiciona .SA se for brasileiro)."""
        ticker = ticker.upper().strip()
        if ticker[-1].isdigit() and len(ticker) >= 5:
            return f"{ticker}.SA"
        return ticker
    
    def _buscar_dados_single(self, ticker: str) -> DadosAtivo:
        """Busca dados de um único ativo (usado internamente)."""
        try:
            ticker_yf = self._formatar_ticker(ticker)
            acao = yf.Ticker(ticker_yf, session=session)
            
            # Busca histórico com timeout
            hist = acao.history(period="5y", timeout=self.timeout)
            if hist.empty:
                return DadosAtivo(ticker, status="erro", mensagem="Sem dados disponíveis")
            
            # Preços ajustados
            adj_close = hist['Adj Close']
            preco_atual = hist['Close'].iloc[-1]
            
            # Cálculos
            preco_medio_12m = adj_close.tail(252).mean() if len(adj_close) >= 252 else adj_close.mean()
            percentil_20 = adj_close.quantile(0.20)
            percentil_80 = adj_close.quantile(0.80)
            minimo_5y = adj_close.min()
            maximo_5y = adj_close.max()
            
            # Variação anual
            if len(adj_close) > 252:
                variacao_anual = (adj_close.iloc[-1] / adj_close.iloc[-252] - 1) * 100
            else:
                variacao_anual = 0.0
            
            # Dividend Yield (últimos 12 meses)
            dy = self._calcular_dy(acao, preco_atual)
            
            return DadosAtivo(
                ticker=ticker,
                preco_atual=preco_atual,
                status="ok",
                mensagem="Atualizado",
                preco_medio_12m=preco_medio_12m,
                percentil_20=percentil_20,
                percentil_80=percentil_80,
                minimo_5y=minimo_5y,
                maximo_5y=maximo_5y,
                variacao_anual=variacao_anual,
                dividend_yield=dy,
                historico=hist
            )
        except Exception as e:
            return DadosAtivo(ticker, status="erro", mensagem=str(e))
    
    def _calcular_dy(self, acao: yf.Ticker, preco_atual: float) -> Optional[float]:
        """Calcula Dividend Yield dos últimos 12 meses."""
        try:
            dividends = acao.dividends
            if dividends.empty or preco_atual <= 0:
                return None
            um_ano_atras = datetime.now() - timedelta(days=365)
            dividends_12m = dividends[dividends.index >= um_ano_atras].sum()
            if dividends_12m > 0:
                return (dividends_12m / preco_atual) * 100
            return None
        except:
            return None
    
    def buscar_precos_batch(self, tickers: List[str],
                            progress_callback: Optional[Callable[[float], None]] = None) -> Dict[str, DadosAtivo]:
        """
        Busca preços de múltiplos ativos em paralelo.
        Retorna dicionário {ticker: DadosAtivo}.
        """
        resultados = {}
        total = len(tickers)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._buscar_dados_single, t): t for t in tickers}
            
            for i, future in enumerate(as_completed(futures)):
                ticker = futures[future]
                try:
                    resultados[ticker] = future.result()
                except Exception as e:
                    resultados[ticker] = DadosAtivo(ticker, status="erro", mensagem=str(e))
                
                if progress_callback:
                    progress_callback((i + 1) / total)
        
        return resultados
    
    @st.cache_data(ttl=settings.YF_CACHE_TTL)
    def get_preco_cached(self, ticker: str) -> Tuple[float, str, str]:
        """Versão cacheada para compatibilidade com código antigo."""
        dados = self._buscar_dados_single(ticker)
        return dados.preco_atual, dados.status, dados.mensagem
