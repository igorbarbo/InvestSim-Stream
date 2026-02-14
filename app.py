import streamlit as st
import pandas as pd
import yfinance as yf
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import numpy as np
import io

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Igorbarbo V8 Ultimate", layout="wide")

# Estilização Luxury
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: white; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    .stProgress > div > div > div > div { background-color: #D4AF37 !important; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'serif'; }
    .stDataFrame { background-color: #0F1116; border-radius: 10px; }
    .stButton button { background-color: #D4AF37; color: black; font-weight: bold; }
    .stButton button:hover { background-color: #B8860B; }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('invest_v8.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ativos 
                 (ticker TEXT PRIMARY KEY, qtd REAL, pm REAL, setor TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS metas_alocacao
                 (classe TEXT PRIMARY KEY, percentual REAL)''')
    conn.commit()
    return conn

conn = init_db()

# --- FUNÇÕES CRUD ---
def salvar_ativo(t, q, p, s):
    if not t or len(t.strip()) < 2:
        st.error("❌ Ticker inválido!")
        return False
    if q <= 0:
        st.error("❌ Quantidade inválida!")
        return False
    if p <= 0:
        st.error("❌ Preço inválido!")
        return False
    try:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO ativos VALUES (?, ?, ?, ?)", 
                  (t.upper().strip(), float(q), float(p), s))
        conn.commit()
        st.success(f"✅ {t.upper()} salvo!")
        time.sleep(1)
        return True
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        return False

def excluir_ativo(t):
    try:
        c = conn.cursor()
        c.execute("DELETE FROM ativos WHERE ticker = ?", (t,))
        conn.commit()
        st.success(f"✅ {t} excluído!")
        return True
    except:
        return False

def atualizar_ativo(t, q, p, s):
    try:
        c = conn.cursor()
        c.execute("UPDATE ativos SET qtd=?, pm=?, setor=? WHERE ticker=?", 
                  (float(q), float(p), s, t.upper().strip()))
        conn.commit()
        st.success(f"✅ {t} atualizado!")
        return True
    except:
        return False

# --- SESSION STATE ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
    st.session_state.etapa_carteira = 1
    st.session_state.valor_investir = 1000.0
    st.session_state.perfil_usuario = "Moderado"
    st.session_state.metas_alocacao = {}
    st.session_state.alertas = {}

# --- LOGIN ---
if not st.session_state.logado:
    st.title("🏛️ Acesso Restrito")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha == "1234":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha Incorreta")
    st.stop()

# --- PREÇOS ---
@st.cache_data(ttl=300)
def pegar_preco(ticker):
    try:
        acao = yf.Ticker(f"{ticker}.SA")
        hist = acao.history(period="2d")
        if hist.empty:
            return 0.0
        return hist['Close'].iloc[-1]
    except:
        return 0.0

# --- ANÁLISE AVANÇADA ---
def calcular_preco_teto_bazin(ticker, dy_desejado=0.06):
    try:
        acao = yf.Ticker(f"{ticker}.SA")
        dividends = acao.dividends.tail(12)
        if dividends.empty:
            return None
        dividendo_anual = dividends.mean() * 4
        return dividendo_anual / dy_desejado
    except:
        return None

def analisar_concentracao_setorial(df):
    if df.empty:
        return []
    total = df['total'].sum()
    setores = df.groupby('setor')['total'].sum() / total * 100
    alertas = []
    for setor, pct in setores.items():
        if pct > 50:
            alertas.append(f"🚨 CRÍTICO: {pct:.1f}% em {setor}")
        elif pct > 30:
            alertas.append(f"⚠️ ALTO: {pct:.1f}% em {setor}")
    return alertas

def exportar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# --- MENU ---
menu = st.sidebar.radio("Navegação", [
    "🏠 Dashboard",
    "🎯 Montar Carteira",
    "💰 Preço Teto",
    "📥 Exportar",
    "⚙️ Gestão"
])

# ============================================
# DASHBOARD
# ============================================
if menu == "🏠 Dashboard":
    st.title("🏛️ Patrimônio")
    
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()
    
    df = pd.read_sql_query("SELECT * FROM ativos", conn)
    
    if not df.empty:
        precos = []
        for ticker in df['ticker']:
            precos.append(pegar_preco(ticker))
        
        df['preco'] = precos
        df['total'] = df['qtd'] * df['preco']
        df['lucro'] = (df['preco'] - df['pm']) * df['qtd']
        
        total = df['total'].sum()
        st.metric("Patrimônio Total", f"R$ {total:,.2f}")
        
        # Alertas setoriais
        alertas = analisar_concentracao_setorial(df)
        if alertas:
            with st.expander("⚠️ Alertas"):
                for a in alertas:
                    st.warning(a)
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.pie(df, values='total', names='ticker', title='Por Ativo')
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.pie(df, values='total', names='setor', title='Por Setor')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Tabela
        st.dataframe(df[['ticker', 'qtd', 'pm', 'preco', 'total', 'lucro']])
    else:
        st.info("Carteira vazia")

# ============================================
# MONTAR CARTEIRA
# ============================================
elif menu == "🎯 Montar Carteira":
    st.title("🎯 Monte sua Carteira")
    
    etapa = st.session_state.etapa_carteira
    
    if etapa == 1:
        st.subheader("Passo 1: Perfil")
        valor = st.number_input("Valor (R$)", value=1000.0)
        perfil = st.selectbox("Perfil", ["Conservador", "Moderado", "Arrojado"])
        
        if st.button("Próximo"):
            st.session_state.valor_investir = valor
            st.session_state.perfil_usuario = perfil
            st.session_state.etapa_carteira = 2
            st.rerun()
    
    elif etapa == 2:
        st.subheader("Passo 2: Alocação")
        perfil = st.session_state.perfil_usuario
        
        if perfil == "Conservador":
            alocacao = {"Renda Fixa": 70, "FIIs": 20, "Ações": 10}
        elif perfil == "Moderado":
            alocacao = {"Renda Fixa": 40, "FIIs": 35, "Ações": 25}
        else:
            alocacao = {"Renda Fixa": 20, "FIIs": 40, "Ações": 40}
        
        st.json(alocacao)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Voltar"):
                st.session_state.etapa_carteira = 1
                st.rerun()
        with col2:
            if st.button("Confirmar"):
                st.session_state.metas_alocacao = alocacao
                st.session_state.etapa_carteira = 3
                st.rerun()
    
    elif etapa == 3:
        st.subheader("✅ Carteira Montada!")
        st.write(f"**Perfil:** {st.session_state.perfil_usuario}")
        st.write(f"**Valor:** R$ {st.session_state.valor_investir:,.2f}")
        
        if st.button("Recomeçar"):
            st.session_state.etapa_carteira = 1
            st.rerun()

# ============================================
# PREÇO TETO
# ============================================
elif menu == "💰 Preço Teto":
    st.title("💰 Preço Teto - Bazin")
    
    df = pd.read_sql_query("SELECT * FROM ativos", conn)
    
    if df.empty:
        st.info("Adicione ativos primeiro")
    else:
        dy = st.slider("DY desejado (%)", 4, 12, 6) / 100
        
        resultados = []
        for ticker in df['ticker']:
            preco_teto = calcular_preco_teto_bazin(ticker, dy)
            preco_atual = pegar_preco(ticker)
            if preco_teto and preco_atual:
                status = "✅ COMPRAR" if preco_atual <= preco_teto else "⏳ ESPERAR"
                resultados.append({
                    'Ticker': ticker,
                    'Atual': preco_atual,
                    'Teto': preco_teto,
                    'Status': status
                })
        
        if resultados:
            st.dataframe(pd.DataFrame(resultados))

# ============================================
# EXPORTAR
# ============================================
elif menu == "📥 Exportar":
    st.title("📥 Exportar Dados")
    
    df = pd.read_sql_query("SELECT * FROM ativos", conn)
    
    if df.empty:
        st.info("Nada para exportar")
    else:
        precos = []
        for ticker in df['ticker']:
            precos.append(pegar_preco(ticker))
        
        df['preco_atual'] = precos
        df['patrimonio'] = df['qtd'] * df['preco_atual']
        
        excel_data = exportar_excel(df)
        st.download_button("📥 Download Excel", excel_data, "carteira.xlsx")

# ============================================
# GESTÃO
# ============================================
elif menu == "⚙️ Gestão":
    st.title("⚙️ Gerenciar")
    
    tab1, tab2 = st.tabs(["➕ Adicionar", "📋 Listar"])
    
    with tab1:
        with st.form("add"):
            ticker = st.text_input("Ticker").upper()
            qtd = st.number_input("Quantidade", min_value=0.01)
            pm = st.number_input("Preço Médio", min_value=0.01)
            setor = st.selectbox("Setor", ["Ação", "FII", "ETF", "RF"])
            if st.form_submit_button("Salvar"):
                salvar_ativo(ticker, qtd, pm, setor)
                st.rerun()
    
    with tab2:
        df = pd.read_sql_query("SELECT * FROM ativos", conn)
        if not df.empty:
            for _, row in df.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{row['ticker']}** - {row['qtd']} cotas - R$ {row['pm']} - {row['setor']}")
                with col2:
                    if st.button("🗑️", key=row['ticker']):
                        excluir_ativo(row['ticker'])
                        st.rerun()
                st.divider()
        else:
            st.info("Nenhum ativo")
