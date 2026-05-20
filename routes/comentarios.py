from flask import Blueprint, request, session, jsonify
from db import get_db
from routes.usuarios import login_requerido

comentarios_bp = Blueprint("comentarios", __name__, url_prefix="/publicaciones")


@comentarios_bp.route("/<int:pub_id>/comentarios", methods=["GET"])
@login_requerido
def listar_comentarios(pub_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT c.*, u.nombre, u.apellido, u.foto_perfil
           FROM comentarios c
           JOIN usuarios u ON u.id = c.usuario_id
           WHERE c.publicacion_id = %s
           ORDER BY c.fecha_publicacion ASC""",
        (pub_id,),
    )
    comentarios = cursor.fetchall()
    cursor.close()
    return jsonify(comentarios), 200


@comentarios_bp.route("/<int:pub_id>/comentarios", methods=["POST"])
@login_requerido
def agregar_comentario(pub_id):
    data = request.get_json()
    if not data.get("contenido"):
        return jsonify({"error": "El contenido es obligatorio"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO comentarios (publicacion_id, usuario_id, contenido) VALUES (%s, %s, %s)",
        (pub_id, session["usuario_id"], data["contenido"]),
    )
    db.commit()
    com_id = cursor.lastrowid
    cursor.close()
    return jsonify({"mensaje": "Comentario agregado", "id": com_id}), 201


@comentarios_bp.route("/<int:pub_id>/comentarios/<int:com_id>", methods=["DELETE"])
@login_requerido
def eliminar_comentario(pub_id, com_id):
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM comentarios WHERE id = %s AND publicacion_id = %s AND usuario_id = %s",
        (com_id, pub_id, uid),
    )
    db.commit()
    afectadas = cursor.rowcount
    cursor.close()
    if afectadas == 0:
        return jsonify({"error": "No encontrado o sin permiso"}), 404
    return jsonify({"mensaje": "Comentario eliminado"}), 200