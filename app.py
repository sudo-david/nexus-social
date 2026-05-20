from flask import Flask
from flask_session import Session
from config import Config
import db

from routes.auth          import auth_bp
from routes.usuarios      import usuarios_bp
from routes.publicaciones import publicaciones_bp
from routes.comentarios   import comentarios_bp
from routes.likes         import likes_bp
from routes.amistades     import amistades_bp
from routes.mensajes      import mensajes_bp
from routes.vistas        import vistas_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Sesiones del lado del servidor
    Session(app)

    # BD
    db.init_app(app)

    # Blueprints
    app.register_blueprint(vistas_bp)       # primero: sirve las páginas
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(publicaciones_bp)
    app.register_blueprint(comentarios_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(amistades_bp)
    app.register_blueprint(mensajes_bp)

    return app

if __name__ == "__main__":
    create_app().run(debug=True)