from flask import Blueprint, request, session, jsonify
from db import get_db
from routes.usuarios import login_requerido

publicaciones_bp = Blueprint("publicaciones", __name__, url_prefix="/publicaciones")


@publicaciones_bp.route("/", methods=["POST"])
@login_requerido
def crear_publicacion():
    data = request.get_json()
    if not data.get("contenido"):
        return jsonify({"error": "El contenido es obligatorio"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO publicaciones (usuario_id, contenido, imagen_url) VALUES (%s, %s, %s)",
        (session["usuario_id"], data["contenido"], data.get("imagen_url")),
    )
    db.commit()
    pub_id = cursor.lastrowid
    cursor.close()
    return jsonify({"mensaje": "Publicación creada", "id": pub_id}), 201


@publicaciones_bp.route("/", methods=["GET"])
@login_requerido
def feed():
    """Devuelve las publicaciones de los amigos aceptados + las propias."""
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT p.*, u.nombre, u.apellido, u.foto_perfil,
                  (SELECT COUNT(*) FROM me_gusta mg WHERE mg.publicacion_id = p.id) AS total_likes,
                  (SELECT COUNT(*) FROM comentarios c WHERE c.publicacion_id = p.id) AS total_comentarios
           FROM publicaciones p
           JOIN usuarios u ON u.id = p.usuario_id
           WHERE p.usuario_id = %s
              OR p.usuario_id IN (
                  SELECT CASE WHEN a.usuario1_id = %s THEN a.usuario2_id ELSE a.usuario1_id END
                  FROM amistades a
                  WHERE (a.usuario1_id = %s OR a.usuario2_id = %s)
                    AND a.estado = 'aceptada'
              )
           ORDER BY p.fecha_publicacion DESC
           LIMIT 50""",
        (uid, uid, uid, uid),
    )
    publicaciones = cursor.fetchall()
    cursor.close()
    return jsonify(publicaciones), 200


@publicaciones_bp.route("/<int:pub_id>", methods=["GET"])
@login_requerido
def obtener_publicacion(pub_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT p.*, u.nombre, u.apellido, u.foto_perfil
           FROM publicaciones p
           JOIN usuarios u ON u.id = p.usuario_id
           WHERE p.id = %s""",
        (pub_id,),
    )
    pub = cursor.fetchone()
    cursor.close()
    if not pub:
        return jsonify({"error": "Publicación no encontrada"}), 404
    return jsonify(pub), 200


@publicaciones_bp.route("/<int:pub_id>", methods=["DELETE"])
@login_requerido
def eliminar_publicacion(pub_id):
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM publicaciones WHERE id = %s AND usuario_id = %s", (pub_id, uid)
    )
    db.commit()
    afectadas = cursor.rowcount
    cursor.close()
    if afectadas == 0:
        return jsonify({"error": "No encontrada o sin permiso"}), 404
    return jsonify({"mensaje": "Publicación eliminada"}), 200