def simulate_investment(initial_amount, monthly_contrib, annual_rate, years):
    """
    Calcula o valor futuro de um investimento com aportes mensais e juros compostos.
    """
    months = int(years * 12)
    value = initial_amount
    for _ in range(months):
        value += monthly_contrib
        value *= (1 + annual_rate/12)
    return round(value, 2)
