def format_currency(value: float | int | None) -> str:
    """
    Formata valores monetários para o padrão brasileiro.
    Exemplo: 1234.5 → R$ 1.234,50
    """
    if value is None:
        return "R$ 0,00"

    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
