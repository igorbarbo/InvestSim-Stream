# database/repository.py
import sqlite3
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from config.settings import settings
from models.ativo import Ativo, LogAuditoria

class DatabaseManager:
    """Gerenciador centralizado de conexões SQLite com migrations e backup."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DB_PATH
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões seguras (auto commit/rollback)."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # acesso por nome de coluna
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Inicializa schema do banco com migrations básicas."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    senha_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Tabela de ativos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ativos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    ticker TEXT NOT NULL,
                    qtd REAL NOT NULL,
                    pm REAL NOT NULL,
                    setor TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de metas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metas_alocacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    classe TEXT NOT NULL,
                    percentual REAL NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    UNIQUE(user_id, classe)
                )
            ''')
            
            # Tabela de alertas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alertas (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    ticker TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    preco REAL NOT NULL,
                    ativo BOOL NOT NULL DEFAULT 1,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de logs de auditoria
            if settings.ENABLE_AUDIT_LOG:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS logs_auditoria (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        acao TEXT NOT NULL,
                        detalhes TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address TEXT,
                        FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE
                    )
                ''')
            
            # Índices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ativos_user ON ativos(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_user ON logs_auditoria(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs_auditoria(timestamp)')
    
    def backup(self) -> str:
        """Cria backup do banco de dados e mantém apenas os últimos 7."""
        backup_dir = Path(settings.BACKUP_DIR)
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"invest_v8_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        
        # Mantém apenas os últimos 7 backups
        backups = sorted(backup_dir.glob("invest_v8_*.db"))
        for old_backup in backups[:-7]:
            old_backup.unlink()
        
        return str(backup_path)


class AtivoRepository:
    """Repositório para operações com ativos."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
    
    def salvar(self, ativo: Ativo, user_id: int) -> bool:
        """Salva ou atualiza um ativo."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM ativos WHERE user_id = ? AND ticker = ?",
                (user_id, ativo.ticker)
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE ativos 
                    SET qtd = ?, pm = ?, setor = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND ticker = ?
                ''', (float(ativo.quantidade), float(ativo.preco_medio), 
                      ativo.setor, user_id, ativo.ticker))
            else:
                cursor.execute('''
                    INSERT INTO ativos (user_id, ticker, qtd, pm, setor)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, ativo.ticker, float(ativo.quantidade), 
                      float(ativo.preco_medio), ativo.setor))
            
            return True
    
    def carregar_por_usuario(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna todos os ativos de um usuário."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM ativos WHERE user_id = ? ORDER BY ticker",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def excluir(self, user_id: int, ticker: str) -> bool:
        """Remove um ativo da carteira."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM ativos WHERE user_id = ? AND ticker = ?",
                (user_id, ticker)
            )
            return cursor.rowcount > 0


class MetaRepository:
    """Repositório para metas de alocação."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
    
    def salvar(self, user_id: int, metas: Dict[str, float]) -> bool:
        """Salva metas para um usuário (substitui as anteriores)."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM metas_alocacao WHERE user_id = ?", (user_id,))
            for classe, percentual in metas.items():
                cursor.execute('''
                    INSERT INTO metas_alocacao (user_id, classe, percentual)
                    VALUES (?, ?, ?)
                ''', (user_id, classe, percentual))
            return True
    
    def carregar(self, user_id: int) -> Dict[str, float]:
        """Retorna as metas do usuário."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT classe, percentual FROM metas_alocacao WHERE user_id = ?",
                (user_id,)
            )
            return {row['classe']: row['percentual'] for row in cursor.fetchall()}


class AlertaRepository:
    """Repositório para alertas de preço."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
    
    def salvar(self, user_id: int, ticker: str, tipo: str, preco: float) -> str:
        """Cria um novo alerta."""
        import uuid
        alerta_id = str(uuid.uuid4())
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alertas (id, user_id, ticker, tipo, preco, ativo)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (alerta_id, user_id, ticker, tipo, preco))
        return alerta_id
    
    def carregar_ativos(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna alertas ativos do usuário."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM alertas WHERE user_id = ? AND ativo = 1",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def desativar(self, alerta_id: str) -> bool:
        """Desativa um alerta (soft delete)."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE alertas SET ativo = 0 WHERE id = ?",
                (alerta_id,)
            )
            return cursor.rowcount > 0


class UsuarioRepository:
    """Repositório para operações com usuários."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
    
    def criar(self, username: str, nome: str, senha_hash: str) -> Optional[int]:
        """Cria um novo usuário e retorna seu ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO usuarios (username, nome, senha_hash)
                    VALUES (?, ?, ?)
                ''', (username, nome, senha_hash))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None
    
    def buscar_por_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retorna usuário pelo nome."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, nome, senha_hash FROM usuarios WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def atualizar_ultimo_login(self, user_id: int):
        """Atualiza timestamp de último login."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuarios SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
