import streamlit as st
import streamlit_authenticator as stauth
from config.settings import settings
from database.repository import DatabaseManager, UsuarioRepository

# 1. Configuração Única
st.set_page_config(page_title="Igorbarbo Private", layout="wide", page_icon="💎")

# 2. Inicialização com Cache de Recurso (Evita loops de inicialização)
@st.cache_resource
def bootstrap_db():
    manager = DatabaseManager()
    manager.backup()
    return manager

db_manager = bootstrap_db()

# 3. Autenticação com Cache de Dados
@st.cache_data(ttl=600)
def get_auth_data():
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, nome, senha_hash FROM usuarios")
        rows = cursor.fetchall()
    return {"usernames": {r['username']: {"name": r['nome'], "password": r['senha_hash']} for r in rows}}

authenticator = stauth.Authenticate(
    get_auth_data(),
    "invest_cookie",
    "secret_key_123", # Use settings.COOKIE_KEY
    30
)

name, authentication_status, username = authenticator.login('main')

if st.session_state["authentication_status"]:
    # Busca ID do usuário uma única vez na sessão
    if 'user_id' not in st.session_state:
        repo = UsuarioRepository(db_manager)
        user = repo.buscar_por_username(st.session_state["username"])
        st.session_state.user_id = user['id']
        repo.atualizar_ultimo_login(user['id'])

    # Interface Sidebar
    st.sidebar.title("💎 IGORBARBO PRIVATE")
    authenticator.logout('Sair', 'sidebar')
    
    menu = st.sidebar.radio("Navegação", [
        "🏠 Dashboard", "💰 Preço Teto", "❄️ Bola de Neve", "⚙️ Gestão"
    ])

    # 4. Roteamento Inteligente (Lazy Loading)
    if menu == "🏠 Dashboard":
        from views.dashboard import show_dashboard
        show_dashboard(st.session_state.user_id)

    elif menu == "💰 Preço Teto":
        from views.preco_teto import show_preco_teto
        show_preco_teto(st.session_state.user_id)

    elif menu == "⚙️ Gestão":
        from views.gestao import show_gestao
        show_gestao(st.session_state.user_id)

elif st.session_state["authentication_status"] is False:
    st.error('Usuário/Senha inválidos')
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, utilize suas credenciais.')
    
