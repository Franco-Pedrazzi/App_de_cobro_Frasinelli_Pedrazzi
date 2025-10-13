from flask import Blueprint, request, redirect, url_for, flash
from py.db import db
from datetime import datetime
import base64

apis = Blueprint("apis", __name__)

class Products(db.Model):
    __tablename__ = "Products"
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric)
    stock = db.Column(db.Integer)
    merchant_email = db.Column(db.String(40), db.ForeignKey('usuario.email'))
    descuentos = db.Column(db.Numeric)
    tipo = db.Column(db.String(50))
    tamano = db.Column(db.BigInteger)
    pixel = db.Column(db.LargeBinary)

class Orders(db.Model):
    __tablename__ = "Orders"
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(40), db.ForeignKey('usuario.email'), nullable=False)
    merchant_email = db.Column(db.String(40), db.ForeignKey('usuario.email'))
    total = db.Column(db.Numeric)
    estado = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime)

class OrderItems(db.Model):
    __tablename__ = "Order_Items"
    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'))
    cantidad = db.Column(db.Integer)

class Payments(db.Model):
    __tablename__ = "Payments"
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'))
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
    print("")
    print(request.files)
    archivo = request.files.get("archivo")

    tipo = ""
    tamano = 0
    pixel = None


    tipo = archivo.content_type
    cont = archivo.read()
    tamano = len(cont)
    pixel = cont
        

    if not data.get("nombre") or not data.get("precio"):
        return "Error: nombre y precio son obligatorios", 400

    nuevo = Products(
        nombre=data.get("nombre"),
        descripcion=data.get("descripcion"),
        precio=float(data.get("precio")),
        stock=int(data.get("stock", 0)),
        merchant_email=data.get("merchant_email"),
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


@apis.route("/products/editar/<int:product_id>", methods=["POST"])
def update_product(product_id):
    producto = Products.query.get(product_id)
    if not producto:
        flash("Producto no encontrado", "error")
        return redirect(request.referrer)

    data = request.form
    for k in ["nombre", "descripcion", "precio", "stock", "merchant_email", "impuestos", "descuentos", "tipo", "tamano", "pixel"]:
        if k in data:
            setattr(producto, k, data[k])
    db.session.commit()
    return flash_and_redirect("Producto actualizado correctamente")

@apis.route("/products/eliminar/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    producto = Products.query.get(product_id)
    if not producto:
        flash("Producto no encontrado", "error")
        return redirect(request.referrer)
    db.session.delete(producto)
    db.session.commit()
    return flash_and_redirect("Producto eliminado correctamente")


# ORDERS
@apis.route("/orders/agregar", methods=["POST"])
def add_order():
    data = request.form
    nuevo = Orders(
        email=data.get("email"),
        merchant_email=data.get("merchant_email"),
        total=data.get("total"),
        estado=data.get("estado"),
        fecha_creacion=datetime.utcnow()
    )
    db.session.add(nuevo)
    db.session.commit()
    return flash_and_redirect("Orden creada correctamente")

@apis.route("/orders/editar/<int:order_id>", methods=["POST"])
def update_order(order_id):
    order = Orders.query.get(order_id)
    if not order:
        flash("Orden no encontrada", "error")
        return redirect(request.referrer)

    data = request.form
    for k in ["email", "merchant_email", "total", "estado"]:
        if k in data:
            setattr(order, k, data[k])
    db.session.commit()
    return flash_and_redirect("Orden actualizada correctamente")

@apis.route("/orders/eliminar/<int:order_id>", methods=["POST"])
def delete_order(order_id):
    order = Orders.query.get(order_id)
    if not order:
        flash("Orden no encontrada", "error")
        return redirect(request.referrer)
    db.session.delete(order)
    db.session.commit()
    return flash_and_redirect("Orden eliminada correctamente")


# ORDER ITEMS
@apis.route("/order_items/agregar", methods=["POST"])
def add_order_item():
    data = request.form
    nuevo = OrderItems(
        order_id=data.get("order_id"),
        product_id=data.get("product_id"),
        cantidad=data.get("cantidad")
    )
    db.session.add(nuevo)
    db.session.commit()
    return flash_and_redirect("Item agregado a la orden correctamente")

@apis.route("/order_items/editar/<int:order_item_id>", methods=["POST"])
def update_order_item(order_item_id):
    item = OrderItems.query.get(order_item_id)
    if not item:
        flash("Item no encontrado", "error")
        return redirect(request.referrer)

    data = request.form
    for k in ["order_id", "product_id", "cantidad"]:
        if k in data:
            setattr(item, k, data[k])
    db.session.commit()
    return flash_and_redirect("Item actualizado correctamente")

@apis.route("/order_items/eliminar/<int:order_item_id>", methods=["POST"])
def delete_order_item(order_item_id):
    item = OrderItems.query.get(order_item_id)
    if not item:
        flash("Item no encontrado", "error")
        return redirect(request.referrer)
    db.session.delete(item)
    db.session.commit()
    return flash_and_redirect("Item eliminado correctamente")


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
