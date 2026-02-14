import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    COOKIE_KEY: str = os.getenv("COOKIE_KEY") or secrets.token_urlsafe(32)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD") or secrets.token_urlsafe(16)
    DB_PATH: str = os.getenv("DB_PATH", "invest_v8_secure.db")
    BACKUP_DIR: str = os.getenv("BACKUP_DIR", "backups")
    YF_CACHE_TTL: int = int(os.getenv("YF_CACHE_TTL", "300"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "10"))
    YF_TIMEOUT: int = int(os.getenv("YF_TIMEOUT", "10"))
    ENABLE_AUDIT_LOG: bool = os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        if len(cls.COOKIE_KEY) < 16:
            raise ValueError("COOKIE_KEY muito curta.")
        return True

settings = Settings()
settings.validate()
