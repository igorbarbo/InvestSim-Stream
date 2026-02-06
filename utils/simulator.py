import pandas as pd

def simulate_investment(
    initial_amt: float,
    monthly_amt: float,
    months: int,
    annual_rate: float
) -> pd.DataFrame:
    """
    Simula o crescimento de um investimento com aporte mensal e taxa anual composta.

    Args:
        initial_amt (float): Valor inicial.
        monthly_amt (float): Valor mensal aportado.
        months (int): Número de meses.
        annual_rate (float): Taxa anual em %.

    Returns:
        pd.DataFrame: DataFrame com colunas ["Mes", "Patrimonio"].
    """

    if months <= 0:
        return pd.DataFrame([{"Mes": 0, "Patrimonio": round(initial_amt, 2)}])

    monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1
    balance = initial_amt
    data = []

    for m in range(1, months + 1):
        balance = balance * (1 + monthly_rate) + monthly_amt
        data.append({"Mes": m, "Patrimonio": round(balance, 2)})

    return pd.DataFrame(data)
