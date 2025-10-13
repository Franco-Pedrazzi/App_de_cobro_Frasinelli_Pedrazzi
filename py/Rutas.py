from flask import render_template,Blueprint
from py.apis import Products

rutas = Blueprint('rutas', __name__,template_folder='templates')

@rutas.route("/")
def Index():   
    products = Products.query.order_by(Products.product_id).all()
    
    return render_template('Index.html',products=products)

@rutas.route("/Add_Player")
def Create_Player():
    return render_template('Add/Add_Player.html')

@rutas.route("/Cantina")
def Cantina():
    return render_template('Add/Cantina.html')
@rutas.route("/Add_Equipo")
def hell():
    return render_template('Add/Add_Equipo.html')

@rutas.route("/Add_Match")
def Create_Match():
    return render_template('Add/Add_Match.html')

@rutas.route("/Add_Staff")
def Create_Staff():
    return render_template('Add/Add_Staff.html')

@rutas.route("/fixture")
def fixture():
    return render_template('fixture.html')



if __name__ == "__main__":
    rutas.run(debug=True)