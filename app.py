import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from modules.database import init_db, connect_db, salvar_ativo
from modules.auth import criar_authenticator
from modules.analise import pegar_preco, analisar_preco_ativo

# 1. Configurações Iniciais
st.set_page_config(page_title="Igorbarbo V10 Ultimate", layout="wide")
init_db()

# 2. Inicialização do Autenticador
auth = criar_authenticator()

# 3. Renderização do Formulário de Login
auth.login(location='main')

# 4. Verificação de Status via Session State (Nova versão stauth)
if st.session_state.get("authentication_status"):
    user = st.session_state["username"]
    name = st.session_state["name"]
    
    # Barra Lateral
    st.sidebar.title(f"💎 {name}")
    menu = st.sidebar.radio("Navegação", ["🏠 Dashboard", "🎯 Assistente", "⚙️ Gestão"])
    auth.logout('Sair do Sistema', 'sidebar')

    # --- PÁGINA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.title("📊 Resumo do Patrimônio")
        conn = connect_db()
        df = pd.read_sql_query(f"SELECT * FROM ativos WHERE user_id='{user}'", conn)
        conn.close()
        
        if not df.empty:
            with st.spinner("Buscando cotações atualizadas..."):
                df['Preço Atual'] = df['ticker'].apply(pegar_preco)
                df['Patrimônio'] = df['qtd'] * df['Preço Atual']
            
            st.metric("Patrimônio Total", f"R$ {df['Patrimônio'].sum():,.2f}")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Sua carteira está vazia. Vá em 'Gestão' para adicionar ativos.")

    # --- PÁGINA: GESTÃO ---
    elif menu == "⚙️ Gestão":
        st.title("⚙️ Gerenciar Ativos")
        with st.form("form_add"):
            c1, c2, c3 = st.columns(3)
            t = c1.text_input("Ticker (ex: PETR4)")
            q = c2.number_input("Quantidade", min_value=0.0)
            p = c3.number_input("Preço Médio", min_value=0.0)
            if st.form_submit_button("Salvar na Carteira"):
                salvar_ativo(user, t, q, p, "Ações")
                st.success(f"{t} salvo com sucesso!")
                st.rerun()

# 5. Tratamento de Erros de Login e Setup Inicial
elif st.session_state.get("authentication_status") is False:
    st.error("Usuário ou senha incorretos.")
    
    # BOTÃO DE EMERGÊNCIA (CORRIGIDO PARA VERSÃO 0.3.0+)
    if st.button("Configurar Primeiro Acesso (Admin)"):
        conn = connect_db()
        # Correção do Hasher: agora usa o método estático .hash()
        hash_senha = stauth.Hasher.hash("1234") 
        try:
            conn.execute("INSERT OR IGNORE INTO usuarios (username, nome, senha_hash) VALUES (?, ?, ?)", 
                         ('admin', 'Igor Barbo', hash_senha))
            conn.commit()
            st.success("Usuário 'admin' criado! Senha: '1234'. Tente logar agora.")
        except Exception as e:
            st.error(f"Erro ao criar banco: {e}")
        finally:
            conn.close()

elif st.session_state.get("authentication_status") is None:
    st.warning("Por favor, faça login para acessar o sistema.")
    
