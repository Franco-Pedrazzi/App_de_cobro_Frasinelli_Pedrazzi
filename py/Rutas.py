from flask import render_template,Blueprint
from py.apis import Products
import base64
from flask_login import current_user
  


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

    return render_template("Index.html", products=products)

@rutas.route("/Producto/<int:product_id>")
def Producto(product_id):
    conexiones = Products.query.filter_by(product_id=product_id).first()

    if not conexiones:
        return render_template('error.html')

    pixels=base64.b64encode(conexiones.pixel).decode("utf-8") if conexiones.pixel else None
    
    return render_template('product.html', Producto=conexiones,pixels=pixels)


if __name__ == "__main__":
    rutas.run(debug=True)