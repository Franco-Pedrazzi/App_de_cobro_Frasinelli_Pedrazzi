from flask import Blueprint, request, redirect, url_for, flash
from py.db import db
from datetime import datetime
from flask_login import current_user
import mercadopago
import traceback
apis = Blueprint("apis", __name__)

access_token = "APP_USR-5796444415198491-100214-0079dab88cf789d8b4614de5bcc470cd-2901193336"
sdk = mercadopago.SDK(access_token)

class Products(db.Model):
    __tablename__ = "Products"
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255))
    descripcion = db.Column(db.String(255))
    precio = db.Column(db.Numeric)
    stock = db.Column(db.Integer)
    merchant_email = db.Column(db.String(40), db.ForeignKey('usuario.email'))
    descuentos = db.Column(db.Numeric)
    tipo = db.Column(db.String(50))
    tamano = db.Column(db.BigInteger)
    pixel = db.Column(db.LargeBinary)


class OrderItems(db.Model):
    __tablename__ = "Order_Items"
    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(40), db.ForeignKey('usuario.email'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'))
    cantidad = db.Column(db.Integer)

class Payments(db.Model):
    __tablename__ = "Payments"
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    monto = db.Column(db.Numeric)
    moneda = db.Column(db.String(255))
    estado = db.Column(db.String(255))
    referencia_gateway = db.Column(db.String(255))
    fecha = db.Column(db.DateTime)

class Notifications(db.Model):
    __tablename__ = "Notifications"
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(40), db.ForeignKey('usuario.email'))
    tipo = db.Column(db.String(255))
    mensaje = db.Column(db.Text)
    estado = db.Column(db.String(255))
    fecha = db.Column(db.DateTime)

class Tickets(db.Model):
    __tablename__ = "Tickets"
    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(40), db.ForeignKey('usuario.email'))
    payment_id = db.Column(db.Integer, db.ForeignKey('Payments.payment_id'))
    asunto = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime)


def flash_and_redirect(msg, tipo="success", destino="index"):
    flash(msg, tipo)
    return redirect(url_for(destino))


@apis.route("/products/agregar", methods=["POST","Get"])
def add_product():
    data = request.form

    
    archivo = request.files.get("archivo")

    tipo = ""
    tamano = 0
    pixel = None


    tipo = archivo.content_type
    cont = archivo.read()
    tamano = len(cont)
    pixel = cont
    print( request.files.get("archivo"),tipo,tamano) 

    if not data.get("nombre") or not data.get("precio"):
        return "Error: nombre y precio son obligatorios", 400

    nuevo = Products(
        nombre=data.get("nombre"),
        descripcion=data.get("descripcion"),
        precio=float(data.get("precio")),
        stock=int(data.get("stock", 0)),
        merchant_email=current_user.email,
        descuentos=data.get("descuentos"),
        tipo=tipo,
        tamano=tamano,
        pixel=pixel
    )

    try:
        db.session.add(nuevo)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"Error al guardar: {e}", 500

    return redirect(url_for("rutas.Index"))


@apis.route("/products/editar/<int:product_id>", methods=["POST","GET"])
def update_product(product_id):
    producto = Products.query.get(product_id)
    data = request.form
    
    producto.descripcion=data.get("decripcion")
    producto.nombre=data.get("nombre")
    producto.precio=data.get("precio")
    producto.stock=data.get("stock")
    db.session.commit()
    return redirect(f"/Producto/{product_id}")

@apis.route("/products/eliminar/<int:product_id>")
def delete_product(product_id):
    producto = Products.query.get(product_id)
    if current_user.email==producto.merchant_email:
        db.session.delete(producto)
        db.session.commit()
    return redirect("/")

@apis.route("/order_items/agregar/<int:product_id>", methods=["POST"])
def add_order_item(product_id):
    data = request.form
    producto = Products.query.get(product_id)
    cantidad=data.get("cantidad")
    if int(cantidad)>producto.stock:
        return redirect(f"/Producto/{product_id}")
    nuevo = OrderItems(
        email=current_user.email,
        product_id=product_id,
        cantidad=cantidad
    )
    db.session.add(nuevo)
    db.session.commit()
    return redirect(f"/Producto/{product_id}")


@apis.route("/orders/update/<int:product_id>", methods=["POST"])
def update_order_item(product_id):
    data = request.form
    cantidad=int(data.get(f"cantidad_{product_id}"))
    producto = Products.query.get(product_id)

    if cantidad>producto.stock:
        return redirect(f"/Producto/{product_id}")
    
    item = OrderItems.query.filter_by(email = current_user.email,product_id = product_id).first()
    item.cantidad=cantidad

    if cantidad<=0:
        print(item.cantidad)
        db.session.delete(item)
    db.session.commit()
    return redirect(f"/carrito")

@apis.route("/orders/eliminar/<int:product_id>")
def delete_order_item(product_id):
    item = OrderItems.query.filter_by(product_id=product_id,email = current_user.email).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(f"/carrito")


@apis.route("/comprar")
def comprar():
    if not current_user.is_authenticated:
        return redirect("/login")

    orders = OrderItems.query.filter_by(email=current_user.email).all()

    items=[]
    for orden in orders:
        producto=Products.query.filter_by(product_id=orden.product_id).first()
        items.append(            {
                "title":producto.nombre ,
                "quantity": int(orden.cantidad),
                "currency_id": "ARS",
                "unit_price": float(producto.precio),
                #"collector_id":
            })

    back_links = {
        "success": "http://localhost:5000/pago/pago_exitoso",
        "failure": "http://localhost:5000/pago/pago_fallido",
        "pending": "http://localhost:5000/pago/pago_pendiente",
    }  
    preference_data = {
        "items":items,"back_urls": back_links,
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        print("Respuesta completa de Mercado Pago:", preference_response)

        if (
            "response" in preference_response
            and "init_point" in preference_response["response"]
        ):
            init_point = preference_response["response"]["init_point"]
            return redirect(init_point)
        else:
            flash("No se pudo generar el checkout. Revisa la consola.", "danger")
            return redirect("/")

    except Exception as e:
        print(" Error al crear la preferencia:", e)
        traceback.print_exc()
        flash("Error al generar el checkout. Revisa la consola.", "danger")
        return redirect("/")





