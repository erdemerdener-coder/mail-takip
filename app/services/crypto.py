"""
Şifreleme yardımcıları.
IMAP şifrelerini Fernet (AES-128-CBC) ile şifreleyerek veritabanında güvenli saklar.
"""
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

_SECRET_KEY = os.getenv("FERNET_KEY")
if not _SECRET_KEY:
    # İlk çalıştırmada otomatik üretilip .env'ye yazılır
    _SECRET_KEY = Fernet.generate_key().decode()
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    with open(env_path, "a", encoding="utf-8") as f:
        f.write(f"\nFERNET_KEY={_SECRET_KEY}\n")

_fernet = Fernet(_SECRET_KEY.encode() if isinstance(_SECRET_KEY, str) else _SECRET_KEY)


def encrypt_password(plain: str) -> str:
    """Düz metin şifreyi Fernet ile şifreler, base64 string döndürür."""
    return _fernet.encrypt(plain.encode()).decode()


def decrypt_password(token: str) -> str:
    """Şifrelenmiş token'ı çözer, düz metin şifreyi döndürür."""
    return _fernet.decrypt(token.encode()).decode()
