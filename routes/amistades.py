from flask import Blueprint, request, session, jsonify
from db import get_db
from routes.usuarios import login_requerido

amistades_bp = Blueprint("amistades", __name__, url_prefix="/amistades")


@amistades_bp.route("/solicitud/<int:receptor_id>", methods=["POST"])
@login_requerido
def enviar_solicitud(receptor_id):
    uid = session["usuario_id"]
    if uid == receptor_id:
        return jsonify({"error": "No puedes enviarte solicitud a ti mismo"}), 400

    # Siempre guardar el menor id como usuario1 para evitar duplicados espejo
    u1, u2 = (uid, receptor_id) if uid < receptor_id else (receptor_id, uid)

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO amistades (usuario1_id, usuario2_id, estado) VALUES (%s, %s, 'pendiente')",
            (u1, u2),
        )
        db.commit()
        return jsonify({"mensaje": "Solicitud enviada"}), 201
    except Exception:
        db.rollback()
        return jsonify({"error": "Ya existe una solicitud o amistad con este usuario"}), 409
    finally:
        cursor.close()


@amistades_bp.route("/solicitud/<int:solicitante_id>", methods=["PUT"])
@login_requerido
def responder_solicitud(solicitante_id):
    """Acepta o rechaza una solicitud. Body: {"accion": "aceptar" | "rechazar"}"""
    uid    = session["usuario_id"]
    data   = request.get_json()
    accion = data.get("accion")

    if accion not in ("aceptar", "rechazar"):
        return jsonify({"error": "Acción inválida. Usa 'aceptar' o 'rechazar'"}), 400

    u1, u2 = (solicitante_id, uid) if solicitante_id < uid else (uid, solicitante_id)

    db = get_db()
    cursor = db.cursor()

    if accion == "aceptar":
        cursor.execute(
            "UPDATE amistades SET estado = 'aceptada' WHERE usuario1_id = %s AND usuario2_id = %s AND estado = 'pendiente'",
            (u1, u2),
        )
        db.commit()
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({"error": "Solicitud no encontrada"}), 404
        mensaje = "Solicitud aceptada"
    else:
        cursor.execute(
            "DELETE FROM amistades WHERE usuario1_id = %s AND usuario2_id = %s AND estado = 'pendiente'",
            (u1, u2),
        )
        db.commit()
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({"error": "Solicitud no encontrada"}), 404
        mensaje = "Solicitud rechazada"

    cursor.close()
    return jsonify({"mensaje": mensaje}), 200


@amistades_bp.route("/", methods=["GET"])
@login_requerido
def listar_amigos():
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT u.id, u.nombre, u.apellido, u.foto_perfil, a.estado, a.fecha_inicio
           FROM amistades a
           JOIN usuarios u ON u.id = CASE
               WHEN a.usuario1_id = %s THEN a.usuario2_id
               ELSE a.usuario1_id
           END
           WHERE (a.usuario1_id = %s OR a.usuario2_id = %s)
             AND a.estado = 'aceptada'""",
        (uid, uid, uid),
    )
    amigos = cursor.fetchall()
    cursor.close()
    return jsonify(amigos), 200


@amistades_bp.route("/pendientes", methods=["GET"])
@login_requerido
def solicitudes_pendientes():
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor(dictionary=True)
    # Solicitudes donde el usuario es receptor (usuario2 si uid > solicitante, usuario1 si uid < solicitante)
    cursor.execute(
        """SELECT u.id, u.nombre, u.apellido, u.foto_perfil, a.fecha_inicio
           FROM amistades a
           JOIN usuarios u ON u.id = CASE
               WHEN a.usuario1_id = %s THEN a.usuario2_id
               ELSE a.usuario1_id
           END
           WHERE (a.usuario1_id = %s OR a.usuario2_id = %s)
             AND a.estado = 'pendiente'""",
        (uid, uid, uid),
    )
    pendientes = cursor.fetchall()
    cursor.close()
    return jsonify(pendientes), 200


@amistades_bp.route("/<int:amigo_id>", methods=["DELETE"])
@login_requerido
def eliminar_amistad(amigo_id):
    uid = session["usuario_id"]
    u1, u2 = (uid, amigo_id) if uid < amigo_id else (amigo_id, uid)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM amistades WHERE usuario1_id = %s AND usuario2_id = %s",
        (u1, u2),
    )
    db.commit()
    afectadas = cursor.rowcount
    cursor.close()
    if afectadas == 0:
        return jsonify({"error": "Amistad no encontrada"}), 404
    return jsonify({"mensaje": "Amistad eliminada"}), 200