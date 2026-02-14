@st.cache_data(ttl=3600) # Cache de 1 hora para preços
def buscar_cotacao_ativo(ticker):
    # lógica de busca na API aqui
    ...
    
# Carregar configurações
from config.settings import settings
from database.repository import DatabaseManager, UsuarioRepository
from services.auditoria_service import AuditoriaService

# Inicializar banco e fazer backup automático (uma vez por dia)
db_manager = DatabaseManager()
db_manager._init_database()
# Backup automático (poderia ser agendado, mas faremos simples aqui)
backup_dir = Path(settings.BACKUP_DIR)
backup_dir.mkdir(exist_ok=True)
db_manager.backup()  # cria backup na inicialização

# Criar usuário admin se não existir
def criar_admin_se_necessario():
    usuario_repo = UsuarioRepository(db_manager)
    admin = usuario_repo.buscar_por_username(settings.ADMIN_USERNAME)
    if not admin:
        hashed = stauth.Hasher.hash(settings.ADMIN_PASSWORD)
        user_id = usuario_repo.criar(settings.ADMIN_USERNAME, "Administrador", hashed)
        if user_id:
            print(f"✅ Usuário admin criado com username: {settings.ADMIN_USERNAME}")
            if not os.getenv("ADMIN_PASSWORD"):
                print(f"   Senha gerada: {settings.ADMIN_PASSWORD}")
        else:
            print("❌ Erro ao criar usuário admin.")

criar_admin_se_necessario()

# Carregar credenciais para autenticador
def carregar_credenciais():
    usuario_repo = UsuarioRepository(db_manager)
    # Infelizmente precisamos de todos os usuários, então vamos buscar
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, nome, senha_hash FROM usuarios")
        rows = cursor.fetchall()
    creds = {"usernames": {}}
    for r in rows:
        creds["usernames"][r['username']] = {
            "name": r['nome'],
            "password": r['senha_hash']
        }
    return creds

# Configurar autenticador
authenticator = stauth.Authenticate(
    carregar_credenciais(),
    "invest_app_cookie",
    settings.COOKIE_KEY,
    30
)

# Login
authenticator.login()

if st.session_state["authentication_status"]:
    username = st.session_state["username"]
    name = st.session_state["name"]
    
    # Buscar user_id
    usuario_repo = UsuarioRepository(db_manager)
    user_info = usuario_repo.buscar_por_username(username)
    if user_info:
        user_id = user_info['id']
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.name = name
        # Atualizar último login
        usuario_repo.atualizar_ultimo_login(user_id)
    else:
        st.error("Usuário não encontrado.")
        st.stop()
    
    authenticator.logout('Sair', 'sidebar')
    st.sidebar.success(f'Bem-vindo, {name}!')
    
    # Menu lateral
    st.sidebar.title("💎 IGORBARBO PRIVATE")
    menu = st.sidebar.radio("Navegação", [
        "🏠 Dashboard",
        "🎯 Montar Carteira",
        "📈 Evolução",
        "🔔 Alertas",
        "📝 Imposto Renda",
        "💰 Preço Teto",
        "📊 Análise Avançada",
        "⚙️ Gestão",
        "❄️ Bola de Neve",
        "🔄 Balanceamento",
        "🔍 Scanner de Oportunidades"
    ])
    
    # Importar views (podem ser carregadas sob demanda)
    from views.dashboard import show_dashboard
    from views.gestao import show_gestao
    from views.assistente import show_assistente
    from views.evolucao import show_evolucao
    from views.alertas import show_alertas
    from views.imposto import show_imposto
    from views.preco_teto import show_preco_teto
    from views.analise_avancada import show_analise_avancada
    from views.bola_neve import show_bola_neve
    from views.balanceamento import show_balanceamento
    from views.scanner import show_scanner
    
    # Roteamento
    if menu == "🏠 Dashboard":
        show_dashboard(user_id)
    elif menu == "⚙️ Gestão":
        show_gestao(user_id)
    elif menu == "🎯 Montar Carteira":
        show_assistente(user_id)
    elif menu == "📈 Evolução":
        show_evolucao(user_id)
    elif menu == "🔔 Alertas":
        show_alertas(user_id)
    elif menu == "📝 Imposto Renda":
        show_imposto(user_id)
    elif menu == "💰 Preço Teto":
        show_preco_teto(user_id)
    elif menu == "📊 Análise Avançada":
        show_analise_avancada(user_id)
    elif menu == "❄️ Bola de Neve":
        show_bola_neve(user_id)
    elif menu == "🔄 Balanceamento":
        show_balanceamento(user_id)
    elif menu == "🔍 Scanner de Oportunidades":
        show_scanner(user_id)
    
    # Rodapé
    st.sidebar.markdown("---")
    from datetime import datetime
    st.sidebar.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.sidebar.caption("💎 Igorbarbo Private Banking v10.0 - Seguro")

elif st.session_state["authentication_status"] == False:
    st.error('Usuário ou senha incorretos')
    st.stop()
else:
    st.warning('Por favor, faça o login')
    st.stop()
