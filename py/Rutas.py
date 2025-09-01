from flask import Flask, render_template,Blueprint, request, jsonify, redirect, url_for
from flask_cors import CORS
from jinja2 import TemplateNotFound

rutas = Blueprint('rutas', __name__,template_folder='templates')



@rutas.route("/signup", methods=["GET"])
def signup_page():
    return render_template('signup and login/signup.html')

@rutas.route("/login", methods=["GET"])
def login_page():
    return render_template('signup and login/login.html')
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



if __name__ == "__main__":
    rutas.run(debug=True)