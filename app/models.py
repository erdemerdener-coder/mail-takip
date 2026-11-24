from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Sender(Base):
    """Gönderen kişi/kurum kartı. Mailler domain/adres bazlı bu tabloya bağlanır."""
    __tablename__ = "senders"

    id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), default="")
    domain = Column(String(255), index=True, default="")
    company_name = Column(String(255), default="")
    # Kategoriler: Müşteri, Tedarikçi, Şirket İçi, Resmi/Hukuk, Genel
    category = Column(String(100), default="Genel")
    # Öncelik: Yüksek, Normal, Düşük
    priority_level = Column(String(50), default="Normal")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)

    emails = relationship("Email", back_populates="sender", cascade="all, delete-orphan")


class Email(Base):
    """Tek bir e-posta kaydı."""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, index=True, nullable=True)
    imap_uid = Column(String(100), index=True, nullable=True)
    sender_id = Column(Integer, ForeignKey("senders.id"), nullable=False)

    from_name = Column(String(255), default="")
    from_email = Column(String(255), index=True, nullable=False)
    to_email = Column(String(255), default="")
    subject = Column(String(500), default="(Konusuz)")
    body_text = Column(Text, default="")
    body_html = Column(Text, default="")

    # Otomatik çıkarılan 1-2 cümlelik içerik özeti
    content_summary = Column(Text, default="")
    # Kullanıcının kendi eklediği özel takip notu
    user_note = Column(Text, default="")

    # Ek dosya bilgisi
    has_attachments = Column(Boolean, default=False)
    attachment_names = Column(String(1000), default="")

    received_at = Column(DateTime, default=_utcnow, index=True)
    is_read = Column(Boolean, default=False)

    # Durumlar: BEKLIYOR, ISLEMDE, TAMAMLANDI, ARSIV (4 durum — plan ile uyumlu)
    status = Column(String(50), default="BEKLIYOR", index=True)

    # Öncelik: YUKSEK, NORMAL, DUSUK
    priority = Column(String(50), default="NORMAL")

    created_at = Column(DateTime, default=_utcnow)

    sender = relationship("Sender", back_populates="emails")


class MailAccount(Base):
    """IMAP ile bağlanan e-posta hesabı. Şifre Fernet ile şifreli saklanır."""
    __tablename__ = "mail_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String(255), unique=True, nullable=False)
    imap_server = Column(String(255), nullable=False)
    imap_port = Column(Integer, default=993)
    use_ssl = Column(Boolean, default=True)
    username = Column(String(255), nullable=False)
    # Fernet ile şifrelenmiş token (düz metin DEĞİL)
    encrypted_password = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
