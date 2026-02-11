def process_metrics(df):
    total_patrimonio = df['Patrimônio'].sum()
    df['Peso'] = df['Patrimônio'] / total_patrimonio
    rent_ponderada = (df['Valorização %'] * df['Peso']).sum()
    df['Prioridade'] = (df['Valorização %'] * -1) * (1 - df['Peso'])
    return df, rent_ponderada, total_patrimonio
  
