import streamlit as st
import pandas as pd
from Modules.database import init_db, connect_db
from Modules.auth import criar_authenticator
from Modules.analise import analisar_preco_ativo, buscar_dados_historicos, calcular_bazin

st.set_page_config(page_title="Igorbarbo V10 Ultimate", layout="wide")
init_db()

auth = criar_authenticator()
name, status, username = auth.login('main')

if status:
    st.sidebar.title(f"Bem-vindo, {name}")
    menu = st.sidebar.radio("Navegação", ["🏠 Dashboard", "🎯 Assistente", "💰 Preço Teto", "⚙️ Gestão"])
    auth.logout('Sair', 'sidebar')

    if menu == "🏠 Dashboard":
        st.title("📊 Patrimônio Global")
        conn = connect_db()
        df = pd.read_sql_query(f"SELECT * FROM ativos WHERE user_id='{username}'", conn)
        
        if not df.empty:
            # Lógica de cálculo de patrimônio em tempo real
            st.dataframe(df) # Exemplo simplificado da tabela estável
        else:
            st.info("Adicione ativos para ver o Dashboard.")

    elif menu == "🎯 Assistente":
        st.title("🎯 Assistente de Alocação")
        valor = st.number_input("Valor para aporte", min_value=0.0)
        perfil = st.selectbox("Perfil", ["Conservador", "Moderado", "Arrojado"])
        
        # Exemplo de Ativo do Passo 3
        ticker_ex = "VALE3"
        hist = buscar_dados_historicos(ticker_ex)
        status_p, cor, desc, score = analisar_preco_ativo(ticker_ex, hist)
        
        st.subheader(f"Análise de {ticker_ex}")
        st.markdown(f"<h3 style='color:{cor}'>{status_p}</h3>", unsafe_allow_html=True)
        st.write(desc)

    elif menu == "⚙️ Gestão":
        st.title("⚙️ Gerenciar Carteira")
        with st.form("add_ativo"):
            t = st.text_input("Ticker")
            q = st.number_input("Quantidade")
            p = st.number_input("Preço Médio")
            s = st.selectbox("Setor", ["Ações", "FIIs", "Renda Fixa"])
            if st.form_submit_button("Salvar"):
                conn = connect_db()
                conn.execute("INSERT INTO ativos (user_id, ticker, qtd, pm, setor) VALUES (?,?,?,?,?)",
                             (username, t.upper(), q, p, s))
                conn.commit()
                st.success("Ativo adicionado!")

elif status is False:
    st.error("Usuário ou senha incorretos.")
  
