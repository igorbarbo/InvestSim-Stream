import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA CHAVE (Sua chave já está aqui!) ---
API_KEY = "AIzaSyAXfzbC-9RGpQgafSG-86AMGK-2AgtOQCU" 

try:
    genai.configure(api_key=API_KEY)
    # Ativando o modelo com busca no Google para notícias em tempo real
    model = genai.GenerativeModel('gemini-1.5-flash', tools=[{'google_search_grounding': {}}])
    IA_ATIVA = True
except:
    IA_ATIVA = False

# --- 2. CONFIGURAÇÃO DE ESTILO DARK PREMIUM ---
st.set_page_config(page_title="Terminal Igorbarbo | Expert", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
        .stApp { background-color: #020408; color: #e0e0e0; }
        [data-testid="stMetric"] { 
            background: rgba(17, 21, 28, 0.7); 
            padding: 20px; border-radius: 15px; border: 1px solid #00ff8833;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.1);
        }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #11151c; border-radius: 10px 10px 0 0; padding: 10px 20px;
        }
    </style>
""", unsafe_allow_True=True)

# --- 3. CARREGAMENTO DE DADOS (Google Sheets) ---
@st.cache_data(ttl=300)
def carregar_dados():
    try:
        url = "https://docs.google.com/spreadsheets/d/1TWfuEvIn9YbSzEyFHKvWWD4XwppHhlj9Cm1RE6BweF8/gviz/tq?tqx=out:csv"
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df.dropna(subset=['Ativo'])
    except:
        return pd.DataFrame()

df_base = carregar_dados()

# --- 4. INTERFACE ---
st.title("⚡ Terminal Igorbarbo | Expert Edition")

tab_dash, tab_ai, tab_radar = st.tabs(["📊 DASHBOARD", "🧠 ANALISTA IA EXPERT", "🎯 RADAR & CALOR"])

with tab_dash:
    if st.button("🚀 SINCRONIZAR MERCADO EM TEMPO REAL"):
        with st.spinner("Conectando aos servidores da Bolsa..."):
            try:
                tickers = df_base['Ativo'].unique().tolist()
                # Busca cotações e o dólar
                dolar = float(yf.download("USDBRL=X", period="1d", progress=False)['Close'].iloc[-1])
                precos = yf.download(tickers, period="1d", progress=False)['Close']
                
                p_dict = {t: float(precos[t].iloc[-1] if len(tickers) > 1 else precos.iloc[-1]) for t in tickers}
                
                df_base['Preço Atual'] = df_base['Ativo'].map(p_dict)
                # Cálculo de patrimônio considerando ativos em dólar se necessário
                df_base['Patrimônio'] = df_base['QTD'] * df_base['Preço Atual']
                df_base['YOC %'] = (df_base['Preço Atual'] / df_base['Preço Médio'] - 1) * 100
                
                st.session_state['df_p'] = df_base
                st.session_state['dolar'] = dolar
                st.success("Tudo atualizado!")
            except Exception as e:
                st.error(f"Erro na sincronização: {e}")

    if 'df_p' in st.session_state:
        df_p = st.session_state['df_p']
        c1, c2, c3 = st.columns(3)
        c1.metric("PATRIMÔNIO TOTAL", f"R$ {df_p['Patrimônio'].sum():,.2f}")
        c2.metric("LUCRO MÉDIO (YOC)", f"{df_p['YOC %'].mean():.2f}%")
        c3.metric("DÓLAR HOJE", f"R$ {st.session_state['dolar']:.2f}")
        
        st.plotly_chart(px.pie(df_p, values='Patrimônio', names='Ativo', hole=.4, template="plotly_dark"), use_container_width=True)
    else:
        st.info("Aperte o botão acima para carregar sua performance.")

with tab_ai:
    st.subheader("💬 Consultor IA com Google Search")
    st.caption("A IA analisará sua carteira e pesquisará notícias em tempo real.")
    
    if prompt := st.chat_input("Ex: Quais notícias de hoje impactam minha carteira?"):
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            if not IA_ATIVA:
                st.error("Erro na ativação da IA.")
            else:
                ctx = st.session_state.get('df_p', df_base).to_string()
                # O Gemini usa o Grounding para pesquisar notícias reais agora
                res = model.generate_content(f"Investidor: Igor. Carteira: {ctx}\n\nPergunta: {prompt}")
                st.write(res.text)

with tab_radar:
    st.subheader("🎯 Mapa de Calor (Heatmap)")
    if 'df_p' in st.session_state:
        df_p = st.session_state['df_p']
        fig = px.treemap(df_p, path=[px.Constant("Minha Carteira"), 'Ativo'], values='Patrimônio', 
                         color='YOC %', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Vá ao Dashboard e sincronize os dados primeiro.")
        
