import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    """
    Genel konfigürasyon sınıfı
    """
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")
    DEBUG = os.environ.get("DEBUG", True)

    # Google AI API Key
    API_KEY = os.environ.get("API_KEY", "")

    # Veritabanı (örnek SQLite, değiştirebilirsin)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI", "sqlite:///smart_grocery.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Online market API ayarları
    GETIR_API_KEY = os.environ.get("GETIR_API_KEY", "")
    MIGROS_API_KEY = os.environ.get("MIGROS_API_KEY", "")

    # Diğer sabitler
    DEFAULT_CALORIES = 2000