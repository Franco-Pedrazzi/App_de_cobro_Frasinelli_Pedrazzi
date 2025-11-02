from flask import Blueprint, request, redirect, url_for, flash
from py.db import db
from datetime import datetime
from flask_login import current_user

apis = Blueprint("apis", __name__)

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


# PRODUCTS
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

# ORDER ITEMS
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


# PAYMENTS
@apis.route("/payments/agregar", methods=["POST"])
def add_payment():
    data = request.form
    nuevo = Payments(
        order_id=data.get("order_id"),
        monto=data.get("monto"),
        moneda=data.get("moneda"),
        estado=data.get("estado"),
        referencia_gateway=data.get("referencia_gateway"),
        fecha=datetime.utcnow()
    )
    db.session.add(nuevo)
    db.session.commit()
    return flash_and_redirect("Pago registrado correctamente")

@apis.route("/payments/editar/<int:payment_id>", methods=["POST"])
def update_payment(payment_id):
    pago = Payments.query.get(payment_id)
    if not pago:
        flash("Pago no encontrado", "error")
        return redirect(request.referrer)

    data = request.form
    for k in ["order_id", "monto", "moneda", "estado", "referencia_gateway"]:
        if k in data:
            setattr(pago, k, data[k])
    db.session.commit()
    return flash_and_redirect("Pago actualizado correctamente")

@apis.route("/payments/eliminar/<int:payment_id>", methods=["POST"])
def delete_payment(payment_id):
    pago = Payments.query.get(payment_id)
    if not pago:
        flash("Pago no encontrado", "error")
        return redirect(request.referrer)
    db.session.delete(pago)
    db.session.commit()
    return flash_and_redirect("Pago eliminado correctamente")


# NOTIFICATIONS
@apis.route("/notifications/agregar", methods=["POST"])
def add_notification():
    data = request.form
    nuevo = Notifications(
        email=data.get("email"),
        tipo=data.get("tipo"),
        mensaje=data.get("mensaje"),
        estado=data.get("estado"),
        fecha=datetime.utcnow()
    )
    db.session.add(nuevo)
    db.session.commit()
    return flash_and_redirect("Notificación creada correctamente")

@apis.route("/notifications/eliminar/<int:notification_id>", methods=["POST"])
def delete_notification(notification_id):
    noti = Notifications.query.get(notification_id)
    if not noti:
        flash("Notificación no encontrada", "error")
        return redirect(request.referrer)
    db.session.delete(noti)
    db.session.commit()
    return flash_and_redirect("Notificación eliminada correctamente")


# TICKETS
@apis.route("/tickets/agregar", methods=["POST"])
def add_ticket():
    data = request.form
    nuevo = Tickets(
        email=data.get("email"),
        payment_id=data.get("payment_id"),
        asunto=data.get("asunto"),
        descripcion=data.get("descripcion"),
        estado=data.get("estado"),
        fecha_creacion=datetime.utcnow()
    )
    db.session.add(nuevo)
    db.session.commit()
    return flash_and_redirect("Ticket creado correctamente")

@apis.route("/tickets/editar/<int:ticket_id>", methods=["POST"])
def update_ticket(ticket_id):
    ticket = Tickets.query.get(ticket_id)
    if not ticket:
        flash("Ticket no encontrado", "error")
        return redirect(request.referrer)

    data = request.form
    for k in ["email", "payment_id", "asunto", "descripcion", "estado"]:
        if k in data:
            setattr(ticket, k, data[k])
    db.session.commit()
    return flash_and_redirect("Ticket actualizado correctamente")

@apis.route("/tickets/eliminar/<int:ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    ticket = Tickets.query.get(ticket_id)
    if not ticket:
        flash("Ticket no encontrado", "error")
        return redirect(request.referrer)
    db.session.delete(ticket)
    db.session.commit()
    return flash_and_redirect("Ticket eliminado correctamente")
