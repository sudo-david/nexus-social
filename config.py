import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambia_esto_en_produccion")
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

    DB_HOST     = os.getenv("DB_HOST", "localhost")
    DB_USER     = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME     = os.getenv("DB_NAME", "red_social")
    DB_PORT     = int(os.getenv("DB_PORT", 3306))