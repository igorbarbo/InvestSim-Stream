def simulate_investment(
    initial_amount,
    monthly_contribution,
    months,
    monthly_yield
):
    balance = initial_amount
    history = []

    for month in range(1, months + 1):
        balance += monthly_contribution
        balance *= (1 + monthly_yield)

        history.append({
            "month": month,
            "balance": round(balance, 2),
            "monthly_income": round(balance * monthly_yield, 2)
        })

    return history
