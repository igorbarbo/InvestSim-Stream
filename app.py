import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InvestSim Pro", layout="wide", page_icon="📈")

st.title("📂 Minha Carteira Pessoal")

# --- FUNÇÃO DE CONEXÃO ---
def carregar_dados():
    try:
        # Link direto de exportação (mais estável para evitar erro 404)
        url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
        df = pd.read_csv(url)
        
        # LIMPEZA: Remove espaços extras nos nomes das colunas
        df.columns = [c.strip() for c in df.columns]
        
        # Remove linhas onde a coluna 'Ativo' está vazia
        if 'Ativo' in df.columns:
            df = df.dropna(subset=['Ativo'])
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return pd.DataFrame()

# --- EXECUÇÃO ---
df_pessoal = carregar_dados()

if not df_pessoal.empty:
    st.success("✅ Planilha carregada com sucesso!")
    
    # Exibe a tabela bruta para conferência
    with st.expander("Ver dados da planilha"):
        st.write(df_pessoal)

    if st.button("📊 Calcular Patrimônio e Lucro"):
        with st.spinner("Buscando cotações no Yahoo Finance..."):
            try:
                # 1. Identifica as colunas (mesmo se houver erro de acento)
                col_qtd = 'QTD' if 'QTD' in df_pessoal.columns else df_pessoal.columns[1]
                col_pm = 'Preço Médio' if 'Preço Médio' in df_pessoal.columns else 'Preco Medio'
                
                # 2. Busca Preços Atuais
                tickers = df_pessoal['Ativo'].unique().tolist()
                dados_mercado = yf.download(tickers, period="1d", progress=False)['Close']
                
                # Ajusta se houver apenas 1 ativo ou vários
                if len(tickers) == 1:
                    precos_atuais = {tickers[0]: dados_mercado.iloc[-1]}
                else:
                    precos_atuais = dados_mercado.iloc[-1].to_dict()

                # 3. Tratamento Numérico
                df_pessoal['QTD'] = pd.to_numeric(df_pessoal[col_qtd], errors='coerce').fillna(0)
                df_pessoal['Preço Pago'] = pd.to_numeric(df_pessoal[col_pm], errors='coerce').fillna(0)
                df_pessoal['Preço Atual'] = df_pessoal['Ativo'].map(precos_atuais)
                
                # 4. Cálculos
                df_pessoal['Investimento'] = df_pessoal['QTD'] * df_pessoal['Preço Pago']
                df_pessoal['Valor Atual'] = df_pessoal['QTD'] * df_pessoal['Preço Atual']
                df_pessoal['Lucro/Prej'] = df_pessoal['Valor Atual'] - df_pessoal['Investimento']

                # --- EXIBIÇÃO ---
                total_geral = df_pessoal['Valor Atual'].sum()
                st.metric("Patrimônio Total", f"R$ {total_geral:,.2f}")

                # Gráfico de Alocação
                fig = px.pie(df_pessoal, values='Valor Atual', names='Ativo', 
                             title="Distribuição da Carteira", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

                # Tabela Final formatada
                st.subheader("Detalhamento por Ativo")
                st.dataframe(df_pessoal.style.format({
                    'Preço Pago': 'R$ {:.2f}', 
                    'Preço Atual': 'R$ {:.2f}', 
                    'Valor Atual': 'R$ {:.2f}',
                    'Lucro/Prej': 'R$ {:.2f}'
                }))

            except Exception as e:
                st.error(f"Erro nos cálculos: {e}")
                st.info("Dica: Verifique se os nomes das colunas na planilha são 'Ativo', 'QTD' e 'Preço Médio'.")

else:
    st.info("Aguardando dados da planilha... Verifique se o link está correto e público.")
    
