# views/assistente.py
import streamlit as st
import pandas as pd
from decimal import Decimal
from database.repository import MetaRepository
from services.preco_service import PrecoService
from services.analise_service import AnaliseService
from utils.graficos import GraficoService
from config.settings import ATIVOS  # você precisará definir esse dicionário em config/settings.py

def show_assistente(user_id):
    st.title("🎯 Assistente Inteligente de Carteira")
    st.markdown("### Meta: Rentabilidade de **8% a 12% ao ano**")
    
    meta_repo = MetaRepository()
    preco_service = PrecoService()
    analise_service = AnaliseService()
    grafico_service = GraficoService()
    
    if 'etapa_assistente' not in st.session_state:
        st.session_state.etapa_assistente = 1
        st.session_state.valor_investir = 1000.0
        st.session_state.perfil_usuario = "Moderado"
        st.session_state.prazo_usuario = "Médio (3-5 anos)"
        st.session_state.objetivo_usuario = "Crescimento patrimonial"
        st.session_state.alocacao_escolhida = None
        st.session_state.retorno_esperado = 0.095
    
    # ETAPA 1: PERFIL
    if st.session_state.etapa_assistente == 1:
        st.markdown("---")
        st.subheader("📋 Passo 1: Conte sobre você")
        col1, col2 = st.columns(2)
        with col1:
            valor = st.number_input("💰 Quanto quer investir? (R$)", min_value=100.0, value=st.session_state.valor_investir, step=500.0)
            perfil = st.selectbox("🎲 Seu perfil de investidor", ["Conservador", "Moderado", "Arrojado"],
                                   index=["Conservador", "Moderado", "Arrojado"].index(st.session_state.perfil_usuario))
        with col2:
            prazo = st.selectbox("⏱️ Prazo do investimento", ["Curto (1-2 anos)", "Médio (3-5 anos)", "Longo (5+ anos)"],
                                 index=["Curto (1-2 anos)", "Médio (3-5 anos)", "Longo (5+ anos)"].index(st.session_state.prazo_usuario))
            objetivo = st.selectbox("🎯 Objetivo principal", ["Crescimento patrimonial", "Geração de renda mensal", "Proteção contra inflação"],
                                    index=["Crescimento patrimonial", "Geração de renda mensal", "Proteção contra inflação"].index(st.session_state.objetivo_usuario))
        if st.button("✅ Próximo: Ver alocação ideal", use_container_width=True):
            st.session_state.valor_investir = valor
            st.session_state.perfil_usuario = perfil
            st.session_state.prazo_usuario = prazo
            st.session_state.objetivo_usuario = objetivo
            st.session_state.etapa_assistente = 2
            st.rerun()
    
    # ETAPA 2: ALOCAÇÃO
    elif st.session_state.etapa_assistente == 2:
        st.markdown("---")
        st.subheader("📊 Passo 2: Alocação recomendada")
        valor = st.session_state.valor_investir
        perfil = st.session_state.perfil_usuario
        
        if perfil == "Conservador":
            alocacao = {"Renda Fixa": {"pct": 70, "retorno": 0.08}, "FIIs": {"pct": 20, "retorno": 0.09}, "Ações": {"pct": 10, "retorno": 0.10}}
        elif perfil == "Moderado":
            alocacao = {"Renda Fixa": {"pct": 40, "retorno": 0.08}, "FIIs": {"pct": 35, "retorno": 0.10}, "Ações": {"pct": 25, "retorno": 0.12}}
        else:
            alocacao = {"Renda Fixa": {"pct": 20, "retorno": 0.08}, "FIIs": {"pct": 40, "retorno": 0.11}, "Ações": {"pct": 40, "retorno": 0.13}}
        
        st.info(f"**Perfil:** {perfil}")
        df_alloc = pd.DataFrame([{"Classe": c, "Percentual": f"{d['pct']}%", "Valor (R$)": f"R$ {valor * d['pct']/100:,.2f}", "Retorno Anual": f"{d['retorno']*100:.1f}%"} for c, d in alocacao.items()])
        st.dataframe(df_alloc, width='stretch')
        
        fig = grafico_service.pizza([d['pct'] for d in alocacao.values()], list(alocacao.keys()), "Distribuição", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
        retorno_total = sum((d['pct']/100) * d['retorno'] for d in alocacao.values())
        renda_mensal = valor * retorno_total / 12
        
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Total", formatar_moeda(valor))
        col_r2.metric("Retorno Anual", f"{retorno_total*100:.1f}%")
        col_r3.metric("Renda Mensal", formatar_moeda(renda_mensal))
        
        if 0.08 <= retorno_total <= 0.12:
            st.success("✅ Dentro da meta de 8% a 12% ao ano!")
        elif retorno_total < 0.08:
            st.warning("⚠️ Abaixo da meta. Considere um perfil mais arrojado.")
        else:
            st.warning("⚠️ Acima da meta. Considere um perfil mais conservador.")
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🔙 Voltar", use_container_width=True):
                st.session_state.etapa_assistente = 1
                st.rerun()
        with col_b2:
            if st.button("✅ Aceitar e escolher ativos", use_container_width=True):
                st.session_state.alocacao_escolhida = alocacao
                st.session_state.retorno_esperado = retorno_total
                st.session_state.etapa_assistente = 3
                st.rerun()
    
    # ETAPA 3: ESCOLHA DE ATIVOS
    elif st.session_state.etapa_assistente == 3:
        st.markdown("---")
        st.subheader("📈 Passo 3: Escolha seus ativos")
        valor = st.session_state.valor_investir
        alocacao = st.session_state.alocacao_escolhida
        carteira_montada = []
        
        from config.settings import ATIVOS  # importa a lista de ativos
        
        for classe, dados in alocacao.items():
            valor_classe = valor * dados['pct'] / 100
            with st.expander(f"### 📌 {classe} - R$ {valor_classe:,.2f} ({dados['pct']}%)", expanded=True):
                st.caption(f"Retorno esperado: {dados['retorno']*100:.1f}% a.a.")
                if classe in ATIVOS:
                    for ativo in ATIVOS[classe]:
                        with st.container():
                            dados_hist = preco_service._buscar_dados_single(ativo['ticker'])
                            resultado = analise_service.analisar(dados_hist)
                            
                            col1, col2, col3, col4, col5 = st.columns([1.2, 2, 1, 1, 1.5])
                            with col1:
                                st.write(f"**{ativo['ticker']}**")
                            with col2:
                                st.write(ativo['nome'][:20] + "...")
                            with col3:
                                st.write(formatar_moeda(ativo['preco']))
                            with col4:
                                st.markdown(f"<span style='color:{resultado.cor}'>{resultado.mensagem[:10]}...</span>", unsafe_allow_html=True)
                            with col5:
                                cotas_max = int(valor_classe // ativo['preco'])
                                if cotas_max > 0:
                                    cotas = st.number_input("Qtd", min_value=0, max_value=cotas_max, value=0, step=1, key=f"qtd_{classe}_{ativo['ticker']}", label_visibility="collapsed")
                                else:
                                    cotas = 0
                                    st.write("💰")
                            if cotas > 0:
                                investimento = cotas * ativo['preco']
                                if investimento <= valor_classe:
                                    carteira_montada.append({
                                        "Classe": classe,
                                        "Ticker": ativo['ticker'],
                                        "Nome": ativo['nome'],
                                        "Preço": ativo['preco'],
                                        "Cotas": cotas,
                                        "Investimento": investimento,
                                        "Status": resultado.status
                                    })
                            st.divider()
        
        if carteira_montada:
            st.markdown("---")
            st.success("### 🎯 Sua carteira montada!")
            df_final = pd.DataFrame(carteira_montada)
            total_investido = df_final['Investimento'].sum()
            sobra = valor - total_investido
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.subheader("📊 Resumo")
                for classe, investido in df_final.groupby('Classe')['Investimento'].sum().items():
                    pct = (investido / valor) * 100
                    st.write(f"**{classe}:** {formatar_moeda(investido)} ({pct:.1f}%)")
            with col_r2:
                st.subheader("📈 Retorno Estimado")
                st.metric("Retorno Anual", f"{st.session_state.retorno_esperado*100:.1f}%")
                renda_mensal = total_investido * st.session_state.retorno_esperado / 12
                st.metric("Renda Mensal", formatar_moeda(renda_mensal))
            
            st.subheader("📋 Ativos Selecionados")
            st.dataframe(df_final[['Ticker', 'Nome', 'Preço', 'Cotas', 'Investimento']], width='stretch')
            
            if sobra > 0:
                st.info(f"💡 Sobra: {formatar_moeda(sobra)}. Você pode aumentar posições ou guardar.")
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button("🔄 Recomeçar", use_container_width=True):
                    st.session_state.etapa_assistente = 1
                    st.rerun()
            with col_b2:
                if st.button("💾 Salvar na Carteira", use_container_width=True):
                    from models.ativo import Ativo
                    from database.repository import AtivoRepository
                    repo = AtivoRepository()
                    for _, ativo in df_final.iterrows():
                        a = Ativo(
                            ticker=ativo['Ticker'],
                            quantidade=Decimal(str(ativo['Cotas'])),
                            preco_medio=Decimal(str(ativo['Preço'])),
                            setor=ativo['Classe']
                        )
                        repo.salvar(a, user_id)
                    st.balloons()
                    st.success("✅ Ativos salvos!")
            with col_b3:
                if st.button("📊 Ver Dashboard", use_container_width=True):
                    st.session_state.etapa_assistente = 1
                    st.rerun()
        else:
            st.info("👆 Selecione as quantidades para montar sua carteira.")
