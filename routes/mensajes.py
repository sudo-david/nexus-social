from flask import Blueprint, request, session, jsonify
from db import get_db
from routes.usuarios import login_requerido

mensajes_bp = Blueprint("mensajes", __name__, url_prefix="/mensajes")


@mensajes_bp.route("/<int:receptor_id>", methods=["POST"])
@login_requerido
def enviar_mensaje(receptor_id):
    data = request.get_json()
    if not data.get("contenido"):
        return jsonify({"error": "El contenido es obligatorio"}), 400

    uid = session["usuario_id"]
    if uid == receptor_id:
        return jsonify({"error": "No puedes enviarte mensajes a ti mismo"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO mensajes (emisor_id, receptor_id, contenido) VALUES (%s, %s, %s)",
        (uid, receptor_id, data["contenido"]),
    )
    db.commit()
    msg_id = cursor.lastrowid
    cursor.close()
    return jsonify({"mensaje": "Mensaje enviado", "id": msg_id}), 201


@mensajes_bp.route("/<int:otro_usuario_id>", methods=["GET"])
@login_requerido
def obtener_conversacion(otro_usuario_id):
    """Devuelve el historial entre el usuario actual y otro usuario."""
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT m.*, 
                  e.nombre AS emisor_nombre, e.foto_perfil AS emisor_foto,
                  r.nombre AS receptor_nombre, r.foto_perfil AS receptor_foto
           FROM mensajes m
           JOIN usuarios e ON e.id = m.emisor_id
           JOIN usuarios r ON r.id = m.receptor_id
           WHERE (m.emisor_id = %s AND m.receptor_id = %s)
              OR (m.emisor_id = %s AND m.receptor_id = %s)
           ORDER BY m.fecha_envio ASC""",
        (uid, otro_usuario_id, otro_usuario_id, uid),
    )
    mensajes = cursor.fetchall()
    cursor.close()
    return jsonify(mensajes), 200


@mensajes_bp.route("/conversaciones", methods=["GET"])
@login_requerido
def listar_conversaciones():
    """Lista los últimos mensajes con cada contacto."""
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT 
               CASE WHEN m.emisor_id = %s THEN m.receptor_id ELSE m.emisor_id END AS contacto_id,
               u.nombre, u.apellido, u.foto_perfil,
               m.contenido AS ultimo_mensaje,
               m.fecha_envio
           FROM mensajes m
           JOIN usuarios u ON u.id = CASE 
               WHEN m.emisor_id = %s THEN m.receptor_id ELSE m.emisor_id END
           WHERE m.id IN (
               SELECT MAX(id) FROM mensajes
               WHERE emisor_id = %s OR receptor_id = %s
               GROUP BY LEAST(emisor_id, receptor_id), GREATEST(emisor_id, receptor_id)
           )
           ORDER BY m.fecha_envio DESC""",
        (uid, uid, uid, uid),
    )
    conversaciones = cursor.fetchall()
    cursor.close()
    return jsonify(conversaciones), 200