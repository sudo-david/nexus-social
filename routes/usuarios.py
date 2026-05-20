from flask import Blueprint, request, session, jsonify
import bcrypt
from db import get_db

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"error": "Autenticación requerida"}), 401
        return f(*args, **kwargs)
    return decorated


@usuarios_bp.route("/<int:usuario_id>", methods=["GET"])
@login_requerido
def obtener_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT id, nombre, apellido, correo, fecha_nacimiento,
                  ubicacion, foto_perfil, fecha_registro
           FROM usuarios WHERE id = %s""",
        (usuario_id,),
    )
    usuario = cursor.fetchone()
    cursor.close()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(usuario), 200


@usuarios_bp.route("/buscar", methods=["GET"])
@login_requerido
def buscar_usuarios():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Parámetro de búsqueda requerido"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)
    like = f"%{q}%"
    cursor.execute(
        """SELECT id, nombre, apellido, correo, foto_perfil
           FROM usuarios
           WHERE nombre LIKE %s OR apellido LIKE %s OR correo LIKE %s""",
        (like, like, like),
    )
    resultados = cursor.fetchall()
    cursor.close()
    return jsonify(resultados), 200


@usuarios_bp.route("/perfil", methods=["PUT"])
@login_requerido
def actualizar_perfil():
    data = request.get_json()
    uid  = session["usuario_id"]
    db   = get_db()
    cursor = db.cursor()

    campos_permitidos = ["nombre", "apellido", "ubicacion", "foto_perfil"]
    sets   = []
    valores = []

    for campo in campos_permitidos:
        if campo in data:
            sets.append(f"{campo} = %s")
            valores.append(data[campo])

    if "contrasena" in data:
        hashed = bcrypt.hashpw(data["contrasena"].encode(), bcrypt.gensalt())
        sets.append("contrasena = %s")
        valores.append(hashed.decode())

    if not sets:
        return jsonify({"error": "Nada que actualizar"}), 400

    valores.append(uid)
    cursor.execute(f"UPDATE usuarios SET {', '.join(sets)} WHERE id = %s", valores)
    db.commit()
    cursor.close()
    return jsonify({"mensaje": "Perfil actualizado"}), 200