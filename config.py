from datetime import timedelta
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY não configurada. Configure no arquivo .env"
        )

    DATABASE_URL = os.environ.get('DATABASE_URL')

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL não configurada. Configure no arquivo .env"
        )
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION = timedelta(hours=8)
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)