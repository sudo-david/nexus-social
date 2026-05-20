import mysql.connector
from flask import g, current_app

def get_db():
    """Retorna la conexión de BD asociada al contexto de la petición actual."""
    if "db" not in g:
        cfg = current_app.config
        g.db = mysql.connector.connect(
            host=cfg["DB_HOST"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            port=cfg["DB_PORT"],
        )
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)