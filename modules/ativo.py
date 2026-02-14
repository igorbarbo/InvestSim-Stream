# models/ativo.py
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional
from datetime import datetime
import re

class Ativo(BaseModel):
    """Modelo de validação para ativos financeiros."""
    
    ticker: str = Field(..., description="Código do ativo na bolsa")
    quantidade: Decimal = Field(..., gt=0, description="Quantidade de cotas/ações")
    preco_medio: Decimal = Field(..., gt=0, description="Preço médio de aquisição")
    setor: str = Field(..., description="Classe/Setor do ativo")
    data_aquisicao: Optional[datetime] = Field(default_factory=datetime.now)
    
    @validator('ticker')
    def validar_ticker(cls, v):
        """Valida formato do ticker (Brasil ou internacional)."""
        v = v.upper().strip()
        # Padrão: 4 letras + número (3,4,11) ou tickers internacionais (letras)
        if not re.match(r'^[A-Z]{4}(3|4|11)$|^[A-Z]{1,5}$', v):
            raise ValueError(f"Ticker inválido: {v}. Use formato B3 (PETR4) ou internacional (AAPL)")
        return v
    
    @validator('setor')
    def validar_setor(cls, v):
        """Normaliza nome do setor."""
        setores_validos = [
            "Ações", "FII Papel", "FII Tijolo", "ETF", 
            "Renda Fixa", "BDR", "Cripto", "Internacional"
        ]
        v = v.strip()
        if v not in setores_validos:
            raise ValueError(f"Setor deve ser um dos: {', '.join(setores_validos)}")
        return v
    
    def to_db_tuple(self, user_id: int) -> tuple:
        """Converte para formato do banco de dados."""
        return (
            user_id,
            self.ticker,
            float(self.quantidade),
            float(self.preco_medio),
            self.setor,
            self.data_aquisicao.isoformat()
        )
    
    @property
    def ticker_yfinance(self) -> str:
        """Retorna ticker formatado para yfinance (adiciona .SA se for brasileiro)."""
        if self.ticker[-1].isdigit() and len(self.ticker) >= 5:
            return f"{self.ticker}.SA"
        return self.ticker


class MetaAlocacao(BaseModel):
    """Modelo para metas de alocação por classe."""
    
    classe: str
    percentual: Decimal = Field(..., ge=0, le=100)
    
    @validator('percentual')
    def validar_percentual(cls, v):
        return round(v, 2)


class LogAuditoria(BaseModel):
    """Modelo para logs de auditoria."""
    
    user_id: int
    acao: str = Field(..., max_length=50)
    detalhes: Optional[str] = Field(None, max_length=500)
    timestamp: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = None
