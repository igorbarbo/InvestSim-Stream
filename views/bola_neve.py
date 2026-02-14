# views/bola_neve.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.exportacao import formatar_moeda

def show_bola_neve(user_id):
    st.title("❄️ Efeito Bola de Neve")
    st.markdown("### Simule o crescimento do seu patrimônio com aportes mensais")
    
    col1, col2 = st.columns(2)
    with col1:
        valor_inicial = st.number_input("💰 Valor inicial (R$)", min_value=0.0, value=0.0, step=1000.0)
        aporte_mensal = st.number_input("📅 Aporte mensal (R$)", min_value=0.0, value=500.0, step=100.0)
    with col2:
        taxa_anual = st.slider("📈 Rentabilidade anual (%)", 0.0, 20.0, 10.0, step=0.5) / 100
        anos = st.slider("⏳ Período (anos)", 1, 50, 20)
    
    meses = anos * 12
    taxa_mensal = (1 + taxa_anual) ** (1/12) - 1
    
    df_sim = pd.DataFrame({'Mês': range(1, meses+1)})
    
    # Com reinvestimento
    patrim = []
    atual = valor_inicial
    for i in range(meses):
        atual = atual * (1 + taxa_mensal) + aporte_mensal
        patrim.append(atual)
    df_sim['Com reinvestimento'] = patrim
    
    # Sem reinvestimento
    patrim_sem = []
    atual_sem = valor_inicial
    for i in range(meses):
        atual_sem = atual_sem + aporte_mensal
        patrim_sem.append(atual_sem)
    df_sim['Sem reinvestimento'] = patrim_sem
    
    final_com = df_sim['Com reinvestimento'].iloc[-1]
    final_sem = df_sim['Sem reinvestimento'].iloc[-1]
    total_aportado = valor_inicial + aporte_mensal * meses
    lucro_com = final_com - total_aportado
    lucro_sem = final_sem - total_aportado
    diferenca = final_com - final_sem
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total aportado", formatar_moeda(total_aportado))
    col_m2.metric("Com reinvestimento", formatar_moeda(final_com), delta=f"Lucro: {formatar_moeda(lucro_com)}")
    col_m3.metric("Sem reinvestimento", formatar_moeda(final_sem), delta=f"Lucro: {formatar_moeda(lucro_sem)}")
    
    st.info(f"💡 **Diferença:** Se gastar os rendimentos, deixará de ganhar **{formatar_moeda(diferenca)}** em {anos} anos.")
    
    fig = px.line(df_sim, x='Mês', y=['Com reinvestimento', 'Sem reinvestimento'],
                  title=f"Crescimento em {anos} anos",
                  labels={'value': 'Patrimônio (R$)', 'variable': 'Cenário'},
                  color_discrete_map={'Com reinvestimento': '#D4AF37', 'Sem reinvestimento': '#FF4B4B'})
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📊 Ver tabela anual"):
        df_sim['Ano'] = ((df_sim['Mês'] - 1) // 12) + 1
        df_anual = df_sim.groupby('Ano').last().reset_index()
        df_anual = df_anual[['Ano', 'Com reinvestimento', 'Sem reinvestimento']]
        df_anual.columns = ['Ano', 'Com reinvestimento', 'Sem reinvestimento']
        df_anual['Com reinvestimento'] = df_anual['Com reinvestimento'].apply(formatar_moeda)
        df_anual['Sem reinvestimento'] = df_anual['Sem reinvestimento'].apply(formatar_moeda)
        st.table(df_anual)
