import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="InvestSim - Projeto Liberdade", layout="wide", page_icon="💰")

st.title("💰 Simulador de Bola de Neve e Liberdade Financeira")

# --- SIDEBAR: CONFIGURAÇÕES DO PLANO ---
st.sidebar.header("🗓️ Planejamento de Longo Prazo")
aporte_mensal = st.sidebar.number_input("Aporte Mensal (R$)", value=3000.0, step=100.0)
anos_projeção = st.sidebar.slider("Anos de Investimento", 1, 30, 10)
taxa_mensal = st.sidebar.slider("Rendimento Mensal Esperado (%)", 0.0, 2.0, 0.8) / 100

def carregar_dados():
    try:
        url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df.dropna(subset=['Ativo'])
    except:
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    if st.button("📈 Simular Evolução de 10 Anos"):
        with st.spinner("Calculando juros compostos..."):
            # 1. Obter Patrimônio Atual
            cotacao_dolar = float(yf.download("USDBRL=X", period="1d", progress=False)['Close'].iloc[-1])
            tickers = df['Ativo'].unique().tolist()
            dados_mercado = yf.download(tickers, period="1d", progress=False)['Close']
            
            precos_dict = {t: float(dados_mercado[t].iloc[-1] if len(tickers) > 1 else dados_mercado.iloc[-1]) for t in tickers}
            df['Preço BRL'] = df['Ativo'].apply(lambda x: precos_dict.get(x, 0) * (cotacao_dolar if not x.endswith(".SA") else 1))
            patrimonio_inicial = (df['QTD'] * df['Preço BRL']).sum()

            # 2. Simulação Mês a Mês
            meses = anos_projeção * 12
            dados_simulacao = []
            patrimonio_acumulado = patrimonio_inicial

            for mes in range(1, meses + 1):
                dividendos_mes = patrimonio_acumulado * taxa_mensal
                patrimonio_acumulado += aporte_mensal + dividendos_mes
                
                dados_simulacao.append({
                    "Mês": mes,
                    "Patrimônio": patrimonio_acumulado,
                    "Dividendos Mensais": dividendos_mes,
                    "Aporte Total": aporte_mensal * mes + patrimonio_inicial
                })

            df_simul = pd.DataFrame(dados_simulacao)

            # --- RESULTADOS FINAIS ---
            resumo_final = df_simul.iloc[-1]
            
            st.subheader(f"📊 Resultado após {anos_projeção} anos")
            c1, c2, c3 = st.columns(3)
            c1.metric("Patrimônio Final", f"R$ {resumo_final['Patrimônio']:,.2f}")
            c2.metric("Renda Mensal Estimada", f"R$ {resumo_final['Dividendos Mensais']:,.2f}")
            c3.metric("Total de Dividendos no Mês", f"R$ {resumo_final['Dividendos Mensais']:,.2f}")

            # --- GRÁFICOS DE EVOLUÇÃO ---
            st.write("### 📈 Evolução do Patrimônio e Renda Passiva")
            fig_evol = px.area(df_simul, x="Mês", y="Patrimônio", title="Crescimento do Patrimônio (Bola de Neve)")
            st.plotly_chart(fig_evol, use_container_width=True)
            
            fig_div = px.line(df_simul, x="Mês", y="Dividendos Mensais", title="Evolução da Renda Mensal (Dividendos para Reinvestir)")
            st.plotly_chart(fig_div, use_container_width=True)

            # --- TABELA DE REINVESTIMENTO ---
            st.write("### 📅 Tabela de Projeção (Primeiros 12 meses)")
            st.dataframe(df_simul.head(12).style.format({
                "Patrimônio": "R$ {:.2f}",
                "Dividendos Mensais": "R$ {:.2f}",
                "Aporte Total": "R$ {:.2f}"
            }))

            st.success(f"Dica: Ao final de {anos_projeção} anos, você estará recebendo R$ {resumo_final['Dividendos Mensais']:,.2f} todo mês sem precisar trabalhar!")

else:
    st.info("Aguardando dados da planilha...")
    
