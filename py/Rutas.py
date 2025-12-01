from flask import render_template,Blueprint,request, redirect
from py.apis import Products,OrderItems
import base64
from flask_login import current_user
from py.db import db


rutas = Blueprint('rutas', __name__,template_folder='templates')


@rutas.route("/")
def Index():   
    productos = Products.query.order_by(Products.product_id).all()
    
    products = []
    for p in productos:
        products.append({
            "product_id":p.product_id,
            "nombre": p.nombre,
            "precio": p.precio,
            "tipo": p.tipo, 
            "pixel": base64.b64encode(p.pixel).decode("utf-8") if p.pixel else None
        })

    return render_template("Index.html", products=products,text="")

@rutas.route("/Producto/<int:product_id>")
def Producto(product_id):
    conexiones = Products.query.filter_by(product_id=product_id).first()
    orden={"cantidad":0}
    if current_user.is_authenticated:
        orden=OrderItems.query.filter_by(email=current_user.email,product_id=product_id).first()
    if not conexiones:
        return render_template('error.html')

    pixels=base64.b64encode(conexiones.pixel).decode("utf-8") if conexiones.pixel else None
    
    return render_template('product.html', Producto=conexiones,pixels=pixels,orden=orden)


@rutas.route("/carrito")
def carrito(): 
    if not current_user.is_authenticated:
        return redirect("/login")  
    productos = Products.query.order_by(Products.product_id).all()
    orders = OrderItems.query.filter_by(email=current_user.email).all()

    productos_dict = {p.product_id: p for p in productos}

    return render_template("carrito.html",products=productos_dict,orders=orders)

@rutas.route("/search",methods=["POST","GET"])
def search():   
    productos = Products.query.order_by(Products.product_id).all()
    data = request.form
    text=data.get("Buscar")   
    products = []
    for p in productos:
        nombre=p.nombre
        div=[""]
        for letra in list(nombre):
            if len( list(div[-1])) < len(list(text)):
                div[-1]=f"{div[-1]}{letra}"
            else:
                div.append(letra)
    
        if text in div:
            products.append({
                "product_id":p.product_id,
                "nombre": p.nombre,
                "precio": p.precio,
                "tipo": p.tipo, 
                "pixel": base64.b64encode(p.pixel).decode("utf-8") if p.pixel else None
            })

    return render_template("search.html", products=products,text=text)

@rutas.route("/pago/<string:re_pago>")
def resultado_pago(re_pago):
    if re_pago =="pago_exitoso":
        items = OrderItems.query.filter_by(email = current_user.email).all()
        for item in items:
            db.session.delete(item)
        db.session.commit()
    return render_template(
        "resultado_pago.html", mensaje=re_pago
    )

if __name__ == "__main__":
    rutas.run(debug=True)