# logic/returns.py

def real_return(amount: float, rate: float, inflation: float) -> float:
    """
    Calcula o retorno real descontando a inflação.
    amount    : Valor futuro nominal
    rate      : Taxa de retorno anual nominal (em decimal)
    inflation : Inflação anual (em decimal)
    """
    # Fórmula do retorno real aproximado
    return amount / ((1 + inflation) ** (1))
