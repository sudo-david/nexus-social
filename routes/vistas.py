from flask import Blueprint, render_template, session, jsonify, redirect, url_for
from db import get_db

vistas_bp = Blueprint("vistas", __name__)


# ── Páginas ──────────────────────────────────────────────────
@vistas_bp.route("/")
def index():
    return redirect(url_for("vistas.feed"))

@vistas_bp.route("/login")
def login():
    return render_template("login.html")

@vistas_bp.route("/registro")
def registro():
    return render_template("registro.html")

@vistas_bp.route("/feed")
def feed():
    return render_template("feed.html")

@vistas_bp.route("/perfil/<int:usuario_id>")
def perfil(usuario_id):
    return render_template("perfil.html")

@vistas_bp.route("/mensajes")
def mensajes():
    return render_template("mensajes.html")


# ── Endpoint auxiliar: usuario actual ────────────────────────
@vistas_bp.route("/usuarios/me")
def me():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, apellido, correo, foto_perfil FROM usuarios WHERE id = %s",
        (session["usuario_id"],),
    )
    u = cursor.fetchone()
    cursor.close()
    if not u:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(u), 200


# ── Endpoint: publicaciones por usuario (para el perfil) ─────
@vistas_bp.route("/publicaciones/usuario/<int:usuario_id>")
def publicaciones_usuario(usuario_id):
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT p.*,
                  (SELECT COUNT(*) FROM me_gusta mg WHERE mg.publicacion_id = p.id) AS total_likes,
                  (SELECT COUNT(*) FROM comentarios c  WHERE c.publicacion_id  = p.id) AS total_comentarios
           FROM publicaciones p
           WHERE p.usuario_id = %s
           ORDER BY p.fecha_publicacion DESC""",
        (usuario_id,),
    )
    pubs = cursor.fetchall()
    cursor.close()
    return jsonify(pubs), 200