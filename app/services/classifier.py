import unicodedata
from typing import Tuple


def _normalize_turkish(text: str) -> str:
    """
    Türkçe İ/I harflerinin .lower() sorununu çözer.
    Python'da 'İ'.lower() → 'i̇' (i + combining dot above) olur ve
    'acil' ile eşleşmez. Bu fonksiyon unicode normalleştirme yapar.
    """
    text = text.replace("İ", "i").replace("I", "ı")
    return unicodedata.normalize("NFC", text.lower())

# Yaygın kişisel e-posta sağlayıcıları (kurumsal değil)
PERSONAL_DOMAINS = {
    "gmail.com", "hotmail.com", "outlook.com", "yahoo.com",
    "yandex.com", "icloud.com", "live.com", "msn.com",
    "protonmail.com", "mail.com", "aol.com",
}

# Türkiye'de yaygın çok parçalı üst düzey alan adı son ekleri
MULTI_PART_TLDS = {
    "com.tr", "org.tr", "net.tr", "gov.tr", "edu.tr",
    "co.uk", "com.au", "co.jp",
}

CATEGORY_KEYWORDS = {
    "Fatura & Finans": [
        "fatura", "odeme", "ödeme", "dekont", "ekstre",
        "tahsilat", "muhasebe", "iban", "invoice", "payment", "receipt",
    ],
    "Müşteri Talebi & Destek": [
        "destek", "support", "yardim", "yardım", "ticket",
        "ariza", "arıza", "sikayet", "şikayet", "problem", "hata",
    ],
    "Teklif & Satış": [
        "teklif", "fiyat", "siparis", "sipariş", "proforma",
        "quote", "order", "anlasma", "anlaşma",
    ],
    "Kargo & Sevkiyat": [
        "kargo", "sevkiyat", "teslimat", "takip no",
        "irsaliye", "shipping", "delivery",
    ],
    "Resmi & Hukuk": [
        "hukuk", "ihtar", "kvkk", "noter", "resmi",
        "avukat", "sözleşme", "sozlesme",
    ],
    "Şirket İçi": [
        "toplanti", "toplantı", "ik", "izin", "duyuru",
        "rapor", "haftalik", "haftalık",
    ],
}

PRIORITY_KEYWORDS = {
    "YUKSEK": [
        "acil", "ivedi", "onemli", "önemli", "kritik",
        "asap", "urgent", "dikkat", "gecikti",
    ],
    "DUSUK": [
        "bulten", "bülten", "newsletter", "kampanya", "reklam",
        "indirim", "firsat", "fırsat", "tanitim", "tanıtım",
    ],
}


def extract_domain_and_company(email_address: str, display_name: str = "") -> Tuple[str, str]:
    """
    E-posta adresinden domain ve şirket/kurum adını çıkarır.

    com.tr gibi çok parçalı TLD'leri doğru işler:
      info@borusan.com.tr      → domain: borusan.com.tr,  company: Borusan
      ahmet@mail.borusan.com.tr → domain: borusan.com.tr, company: Borusan
      kisi@gmail.com            → domain: gmail.com,      company: <display_name veya kullanıcı adı>
    """
    if not email_address or "@" not in email_address:
        return "", display_name or "Bilinmeyen"

    local, domain = email_address.strip().lower().rsplit("@", 1)

    # Kişisel sağlayıcıysa şirket adı yok, kişi adını kullan
    if domain in PERSONAL_DOMAINS:
        company = display_name if display_name else local.replace(".", " ").title()
        return domain, company

    # Çok parçalı TLD kontrolü (com.tr, co.uk vb.)
    parts = domain.split(".")
    tld_candidate = ".".join(parts[-2:]) if len(parts) >= 2 else ""

    if tld_candidate in MULTI_PART_TLDS and len(parts) >= 3:
        # örn: mail.borusan.com.tr → şirket kısmı = parts[-3] = "borusan"
        company_part = parts[-3]
    elif len(parts) >= 2:
        # örn: borusan.com → şirket kısmı = parts[0] = "borusan"
        company_part = parts[0]
    else:
        company_part = domain

    company = company_part.replace("-", " ").replace("_", " ").title()
    return domain, company


def detect_category_and_priority(subject: str, body: str = "") -> Tuple[str, str]:
    """
    Konu ve içerikten otomatik kategori ve öncelik derecesi tespit eder.
    """
    text = _normalize_turkish(f"{subject or ''} {body or ''}")

    # Kategori tespiti
    detected_category = "Genel"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            detected_category = cat
            break

    # Öncelik tespiti
    detected_priority = "NORMAL"
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            detected_priority = priority
            break

    return detected_category, detected_priority


def generate_content_summary(body_text: str, max_length: int = 150) -> str:
    """
    E-posta gövdesinden selamlama, imza ve alıntı satırlarını temizleyip
    anlamlı ilk 1-2 cümleyi döndürür.
    """
    if not body_text:
        return ""

    lines = body_text.strip().splitlines()
    meaningful_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Alıntı satırlarını atla
        if stripped.startswith(">") or stripped.startswith("On ") and "wrote:" in stripped:
            continue
        # Selamlama satırlarını atla
        lower = stripped.lower()
        if any(lower.startswith(g) for g in [
            "merhaba", "sayın", "sevgili", "hi ", "hello", "dear ",
            "iyi günler", "iyi akşamlar",
        ]):
            continue
        # İmza bloğunu atla
        if any(lower.startswith(s) for s in [
            "saygılarımla", "regards", "best regards", "iyi çalışmalar",
            "teşekkürler", "thanks", "tel:", "gsm:", "mob:", "--",
        ]):
            break
        meaningful_lines.append(stripped)

    summary = " ".join(meaningful_lines)
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(" ", 1)[0] + "…"
    return summary
