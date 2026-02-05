import streamlit as st
import pandas as pd
# Importando as funções da sua pasta utils
from utils.simulator import simulate_investment
from utils.market import get_price_history

# 1. Configuração da Página
st.set_page_config(
    page_title="InvestSim - Dashboard Financeiro",
    page_icon="💰",
    layout="wide"
)

# 2. Barra Lateral (Navegação e Avisos)
st.sidebar.title("📌 Menu")
st.sidebar.info("Acesse as páginas no menu acima para ferramentas detalhadas.")

# 3. Cabeçalho Principal
st.title("💰 InvestSim: Seu Futuro Financeiro")
st.markdown("""
Bem-vindo ao seu painel de simulação. Aqui você transforma números em metas reais.
""")

st.divider()

# 4. Área de Simulação Rápida
st.subheader("🚀 Simulação de Crescimento")

col1, col2 = st.columns([1, 2])

with col1:
    st.write("**Parâmetros da Simulação**")
    valor_inicial = st.number_input("Investimento Inicial (R$)", min_value=0.0, value=1000.0, step=100.0)
    aporte_mensal = st.number_input("Aporte Mensal (R$)", min_value=0.0, value=200.0, step=50.0)
    anos = st.slider("Tempo de investimento (Anos)", 1, 40, 10)
    taxa_anual = st.number_input("Taxa de Juros Anual (%)", min_value=0.0, value=10.0, step=0.5)

    meses = anos * 12

with col2:
    # Chamada da função que está em utils/simulator.py
    try:
        df_simulacao = simulate_investment(valor_inicial, aporte_mensal, meses, taxa_anual)
        
        if not df_simulacao.empty:
            total_final = df_simulacao['Patrimônio'].iloc[-1]
            total_investido = valor_inicial + (aporte_mensal * meses)
            lucro_juros = total_final - total_investido

            # Métricas em destaque
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Final", f"R$ {total_final:,.2f}")
            m2.metric("Total Investido", f"R$ {total_investido:,.2f}")
            m3.metric("Ganho em Juros", f"R$ {lucro_juros:,.2f}", delta_color="normal")

            # Gráfico de evolução
            st.line_chart(df_simulacao.set_index("Mês")["Patrimônio"])
        else:
            st.warning("Aguardando dados para gerar a simulação...")
            
    except Exception as e:
        st.error(f"Erro ao processar simulação: {e}")
        st.info("Dica: Verifique se o arquivo utils/simulator.py está correto.")

st.divider()

# 5. Rodapé
st.caption("InvestSim Stream - Desenvolvido para análise educacional de ativos.")
csv = df_simulacao.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar Planilha da Simulação",
    data=csv,
    file_name='simulacao_investimento.csv',
    mime='text/csv',
)

