import pandas as pd
from logic.inflation import annual_to_monthly

def simulate_investment(initial: float, monthly: float, rate_annual: float, months: int):
    """Gera a evolução patrimonial mês a mês."""
    rate_monthly = annual_to_monthly(rate_annual)
    data = []
    current_balance = initial
    
    for month in range(months + 1):
        data.append({"Mês": month, "Patrimônio": current_balance})
        current_balance = (current_balance + monthly) * (1 + rate_monthly)
        
    return pd.DataFrame(data)
  
