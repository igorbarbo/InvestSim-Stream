def calcular_investimento(valor_inicial, aporte_mensal, taxa_anual, meses):
    try:
        # Garante que as entradas sejam números
        v_ini = float(valor_inicial)
        taxa = float(taxa_anual)
        t = int(meses)
        
        taxa_mensal = (1 + taxa)**(1/12) - 1
        total = v_ini * (1 + taxa_mensal)**t
        
        # Retorna apenas o número final, não um DataFrame
        return float(total)
    except Exception as e:
        return 0.0
        
