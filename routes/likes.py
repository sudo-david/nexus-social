from flask import Blueprint, session, jsonify
from db import get_db
from routes.usuarios import login_requerido

likes_bp = Blueprint("likes", __name__, url_prefix="/publicaciones")


@likes_bp.route("/<int:pub_id>/like", methods=["POST"])
@login_requerido
def dar_like(pub_id):
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO me_gusta (usuario_id, publicacion_id) VALUES (%s, %s)",
            (uid, pub_id),
        )
        db.commit()
        return jsonify({"mensaje": "Like agregado"}), 201
    except Exception:
        db.rollback()
        return jsonify({"error": "Ya diste like a esta publicación"}), 409
    finally:
        cursor.close()


@likes_bp.route("/<int:pub_id>/like", methods=["DELETE"])
@login_requerido
def quitar_like(pub_id):
    uid = session["usuario_id"]
    db  = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM me_gusta WHERE usuario_id = %s AND publicacion_id = %s",
        (uid, pub_id),
    )
    db.commit()
    afectadas = cursor.rowcount
    cursor.close()
    if afectadas == 0:
        return jsonify({"error": "No habías dado like"}), 404
    return jsonify({"mensaje": "Like eliminado"}), 200