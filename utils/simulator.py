import pandas as pd

def simulate_investment(initial_amt, monthly_amt, months, annual_rate):
    # Taxa mensal equivalente
    monthly_rate = (1 + annual_rate/100)**(1/12) - 1
    data = []
    balance = initial_amt

    for m in range(1, months + 1):
        balance = balance * (1 + monthly_rate) + monthly_amt
        data.append({"Mês": m, "Patrimônio": round(balance, 2)})

    if not data:
        data = [{"Mês": 0, "Patrimônio": initial_amt}]
        
    return pd.DataFrame(data)
    
