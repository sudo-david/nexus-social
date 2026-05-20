from flask import Blueprint, request, session, jsonify
import bcrypt
from db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    campos = ["nombre", "apellido", "correo", "contrasena", "fecha_nacimiento"]
    if not all(data.get(c) for c in campos):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    hashed = bcrypt.hashpw(data["contrasena"].encode(), bcrypt.gensalt())

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO usuarios (nombre, apellido, correo, contrasena,
               fecha_nacimiento, ubicacion, foto_perfil)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                data["nombre"],
                data["apellido"],
                data["correo"],
                hashed.decode(),
                data["fecha_nacimiento"],
                data.get("ubicacion"),
                data.get("foto_perfil"),
            ),
        )
        db.commit()
        return jsonify({"mensaje": "Usuario registrado correctamente"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 409
    finally:
        cursor.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data.get("correo") or not data.get("contrasena"):
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (data["correo"],))
    usuario = cursor.fetchone()
    cursor.close()

    if not usuario or not bcrypt.checkpw(
        data["contrasena"].encode(), usuario["contrasena"].encode()
    ):
        return jsonify({"error": "Credenciales inválidas"}), 401

    session["usuario_id"] = usuario["id"]
    session["nombre"]     = usuario["nombre"]
    return jsonify({"mensaje": "Sesión iniciada", "usuario_id": usuario["id"]}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada"}), 200