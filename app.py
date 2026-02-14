import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from modules.database import init_db, connect_db, salvar_ativo
from modules.auth import criar_authenticator
from modules.analise import pegar_preco, analisar_preco_ativo

# Configurações iniciais
st.set_page_config(page_title="Igorbarbo V10 Ultimate", layout="wide")
init_db()

# Inicialização do Autenticador
auth = criar_authenticator()
auth.login(location='main')

# Lógica de Acesso
if st.session_state["authentication_status"]:
    user = st.session_state["username"]
    st.sidebar.title(f"💎 {st.session_state['name']}")
    menu = st.sidebar.radio("Navegação", ["🏠 Dashboard", "🎯 Assistente", "⚙️ Gestão"])
    auth.logout('Sair do Sistema', 'sidebar')

    if menu == "🏠 Dashboard":
        st.title("📊 Painel de Patrimônio")
        conn = connect_db()
        df = pd.read_sql_query(f"SELECT * FROM ativos WHERE user_id='{user}'", conn)
        conn.close()
        
        if not df.empty:
            with st.spinner("Atualizando preços em tempo real..."):
                df['Preço Atual'] = df['ticker'].apply(pegar_preco)
                df['Patrimônio'] = df['qtd'] * df['Preço Atual']
            
            st.metric("Total da Carteira", f"R$ {df['Patrimônio'].sum():,.2f}")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Sua carteira está vazia. Adicione ativos na aba Gestão.")

    elif menu == "🎯 Assistente":
        st.title("🎯 Assistente Inteligente")
        tick_input = st.text_input("Digite o Ticker para analisar (ex: PETR4, ITUB4)").upper()
        if tick_input:
            status, cor, desc, score = analisar_preco_ativo(tick_input)
            st.markdown(f"<h2 style='color:{cor}'>{status}</h2>", unsafe_allow_html=True)
            st.info(desc)

    elif menu == "⚙️ Gestão":
        st.title("⚙️ Gerenciar Minha Carteira")
        with st.form("add_ativo_form"):
            c1, c2, c3 = st.columns(3)
            t = c1.text_input("Ticker")
            q = c2.number_input("Quantidade", min_value=0.0)
            p = c3.number_input("Preço Médio", min_value=0.0)
            if st.form_submit_button("Salvar Ativo"):
                salvar_ativo(user, t, q, p, "Ações")
                st.success(f"{t} adicionado com sucesso!")

elif st.session_state["authentication_status"] is False:
    st.error("Usuário ou senha incorretos.")
    # Botão de emergência para criar o primeiro usuário
    if st.button("Configurar Usuário Admin"):
        conn = connect_db()
        # Senha padrão: 1234
        hash_senha = stauth.Hasher(["1234"]).generate()[0]
        conn.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'Igor Barbo', ?)", (hash_senha,))
        conn.commit()
        st.success("Admin 'admin' criado com a senha '1234'. Tente logar agora.")

elif st.session_state["authentication_status"] is None:
    st.warning("Por favor, insira suas credenciais.")
    
