import pandas as pd

def calcular_investimento(
    inicial: float, 
    mensal: float, 
    taxa_anual: float, 
    anos: int
) -> pd.DataFrame:
    """
    Calcula a evolução do patrimônio com aportes mensais e juros compostos.

    Args:
        inicial (float): Valor inicial investido
        mensal (float): Aporte mensal
        taxa_anual (float): Taxa anual em %
        anos (int): Período em anos

    Returns:
        pd.DataFrame: DataFrame com colunas 'Mes', 'Patrimonio Total', 'Total Investido'
    """
    meses = anos * 12
    taxa_mensal = (1 + taxa_anual / 100) ** (1/12) - 1
    saldo = inicial
    dados = []

    for mes in range(0, meses + 1):
        if mes > 0:
            saldo += saldo * taxa_mensal + mensal
        dados.append({
            "Mes": mes,
            "Patrimonio Total": round(saldo, 2),
            "Total Investido": round(inicial + mensal * mes, 2)
        })
    
    return pd.DataFrame(dados)


def obter_taxa_cenario(perfil: str) -> float:
    """
    Retorna a taxa anual sugerida para um perfil de investidor.

    Args:
        perfil (str): 'Conservador', 'Moderado' ou 'Agressivo'

    Returns:
        float: Taxa anual em %
    """
    cenarios = {
        "Conservador": 10.5,
        "Moderado": 13.5,
        "Agressivo": 17.0
    }
    return cenarios.get(perfil, 10.0)
