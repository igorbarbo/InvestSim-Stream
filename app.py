import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="InvestSim - Montagem Real", layout="wide", page_icon="🎯")

# --- ESTILO E TÍTULO ---
st.title("🎯 Montagem de Carteira Híbrida (Dia 1)")
st.subheader("Foco: Renda de 0,8%/mês + Diversificação")

# --- SIDEBAR: O APORTE DE HOJE ---
st.sidebar.header("📥 Seu Aporte")
aporte_disponivel = st.sidebar.number_input("Quanto vai investir hoje? (R$)", value=3000.0)

# --- CONFIGURAÇÃO DA CARTEIRA IDEAL ---
# Definimos os ativos "modelo" que você escolheu
carteira_modelo = {
    'FIIs (40%)': ['HGLG11.SA', 'MXRF11.SA'],
    'Ações BR (30%)': ['PETR4.SA', 'BBAS3.SA', 'TAEE11.SA'],
    'Internacional (30%)': ['IVVB11.SA', 'AAPL34.SA']
}

if st.button("🚀 Gerar Minha Lista de Compras"):
    with st.spinner("Buscando preços atuais no mercado..."):
        # 1. Coleta de Preços
        todos_tickers = [item for sublist in carteira_modelo.values() for item in sublist]
        dados = yf.download(todos_tickers, period="1d", progress=False)['Close']
        precos = {t: float(dados[t].iloc[-1]) for t in todos_tickers}

        # 2. Distribuição do Dinheiro (Aporte de R$ 3000)
        # 40% FIIs = 1200 | 30% BR = 900 | 30% Inter = 900
        distribuicao = {
            'FII (40%)': aporte_disponivel * 0.40,
            'Ações BR (30%)': aporte_disponivel * 0.30,
            'Internacional (30%)': aporte_disponivel * 0.30
        }

        # 3. Montagem da Tabela de Compras
        lista_compras = []
        
        # Lógica para FIIs
        valor_por_fii = distribuicao['FII (40%)'] / len(carteira_modelo['FIIs (40%)'])
        for ticker in carteira_modelo['FIIs (40%)']:
            preco = precos[ticker]
            qtd = int(valor_por_fii / preco)
            lista_compras.append([ticker, 'FII', preco, qtd, qtd * preco])

        # Lógica para Ações BR
        valor_por_acao = distribuicao['Ações BR (30%)'] / len(carteira_modelo['Ações BR (30%)'])
        for ticker in carteira_modelo['Ações Brasil (30%)' if 'Ações Brasil (30%)' in carteira_modelo else 'Ações BR (30%)']:
            # Pequeno ajuste no nome da chave caso necessário
            pass 
        # Re-ajustando loop para evitar erros de chave:
        for ticker in carteira_modelo['Ações BR (30%)']:
            preco = precos[ticker]
            qtd = int(valor_por_acao / preco)
            lista_compras.append([ticker, 'Ações BR', preco, qtd, qtd * preco])

        # Lógica para Internacional
        valor_por_inter = distribuicao['Internacional (30%)'] / len(carteira_modelo['Internacional (30%)'])
        for ticker in carteira_modelo['Internacional (30%)']:
            preco = precos[ticker]
            qtd = int(valor_por_inter / preco)
            lista_compras.append([ticker, 'Internacional', preco, qtd, qtd * preco])

        df_compras = pd.DataFrame(lista_compras, columns=['Ativo', 'Classe', 'Preço Unit.', 'QTD p/ Comprar', 'Total Sugerido'])

        # --- EXIBIÇÃO ---
        c1, c2 = st.columns([1, 1])

        with c1:
            st.write("### 🛒 O que comprar agora:")
            st.dataframe(df_compras.style.format({'Preço Unit.': 'R$ {:.2f}', 'Total Sugerido': 'R$ {:.2f}'}))
            
            st.success(f"**Total Planejado:** R$ {df_compras['Total Sugerido'].sum():,.2f}")
            st.info(f"**Renda Mensal Estimada deste Aporte:** R$ {df_compras['Total Sugerido'].sum() * 0.008:,.2f}")

        with c2:
            st.write("### 📊 Divisão por Categoria")
            fig = px.pie(df_compras, values='Total Sugerido', names='Classe', hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

        # MENSAGEM FINAL
        st.warning("⚠️ **Dica:** Após comprar esses ativos na sua corretora, não esqueça de anotá-los na sua planilha do Google para o Dashboard acompanhar o lucro em tempo real!")
        
