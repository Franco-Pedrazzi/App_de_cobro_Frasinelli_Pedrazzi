from flask import Blueprint, request, jsonify
from py.db import db 

apis = Blueprint("apis", __name__)


class Example(db.Model):
    __tablename__ = "examples"
    id_example = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), default="-")


@apis.route("/api/example", methods=["POST"])
def add_example():
    data = request.get_json()
    nuevo = Example(nombre=data.get("nombre", "-"))
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(success=True, example={"nombre": nuevo.nombre})


@apis.route("/api/example", methods=["GET"])
def get_example():
    example = Example.query.all()
    return jsonify([
        {"id_example": c.id_example, "nombre": c.nombre}
        for c in example
    ])

