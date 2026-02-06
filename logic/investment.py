# logic/investment.py
import pandas as pd

def calcular_investimento(valor_ini, aporte_mensal, taxa_anual, meses):
    """
    Calcula a evolução de um investimento com aportes mensais.
    Taxa anual é convertida para mensal.
    """
    # Conversão da taxa anual para mensal (Juros Compostos)
    taxa_mensal = (1 + taxa_anual/100)**(1/12) - 1
    
    saldo = valor_ini
    dados = []
    
    for i in range(meses + 1):
        dados.append({
            "Mês": i,
            "Saldo": round(saldo, 2)
        })
        saldo = (saldo + aporte_mensal) * (1 + taxa_mensal)
        
    return pd.DataFrame(dados)
    
