from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

from py.Rutas import rutas
from py.apis import apis
from py.db import db


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/Copa_Renault'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'

db.init_app(app)

app.register_blueprint(rutas)
app.register_blueprint(apis)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

GMAIL_USER = "renaultcup0@gmail.com"
GMAIL_PASS = "ywer mdum zooi zvxm"

@login_manager.user_loader
def load_user(email):
    return Usuario.query.get(email)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, primary_key=True)
    contraseña = db.Column(db.String(100))
    rango = db.Column(db.String(20))

    def get_id(self):
        return self.email 
    
    def is_active(self):
        return True
    

class Verificacion(db.Model):
    __tablename__ = 'verificacion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(40))
    codigo = db.Column(db.String(20))
    nombre = db.Column(db.String(40))
    contra_codificada = db.Column(db.String(200))
    rango = db.Column(db.String(20))

@app.context_processor
def inject_user_rango():
    if current_user.is_authenticated:
        return dict(rango=current_user.rango)
    return dict()
    


@app.route("/check_email", methods=["POST"])
def check_email():
    data = request.get_json()
    email = data.get("Email")
    if not email:
        return jsonify({"exists": False})

    existe = Usuario.query.filter_by(email=email).first() is not None or Verificacion.query.filter_by(email=email).first() is not None
    return jsonify({"exists": existe})

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    nombre = data.get("Nombre")
    email = data.get("Email")
    contraseña = data.get("Contraseña")
    rango = "A"
    usuario = Usuario.query.filter_by(email=email).first()
    if not (nombre and email and contraseña):
        return jsonify({"success": False, "error": "Faltan datos"}), 400

    if usuario:
        if not usuario or not check_password_hash(usuario.contraseña, contraseña):
            return jsonify({"success": False, "error": "El email ya está registrado y contraseña incorrecta"}), 401
        login_user(usuario)
        return jsonify({"success": False, "error": "El email ya está registrado"}), 400
    if Verificacion.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "El email ya está pendiente de verificacion"}), 400
    contra_codificada = generate_password_hash(contraseña)
    codigo = ''.join(random.choices('0123456789', k=6))

    verif = Verificacion(email=email, codigo=codigo, nombre=nombre, contra_codificada=contra_codificada, rango=rango)
    db.session.add(verif)
    db.session.commit()

    enviado = enviar_email(email, codigo)
    if not enviado:
        return jsonify({"success": False, "error": "No se pudo enviar el codigo de verificacion"}), 500

    return jsonify({"success": True, "mensaje": "Código enviado a tu email, verifica para activar tu cuenta."}), 200

@app.route("/verificar_codigo", methods=["POST"])
def verificar_codigo():
    data = request.get_json()
    email = data.get("Email")
    codigo = data.get("Codigo")

    if not (email and codigo):
        return jsonify({"success": False, "error": "Faltan datos"}), 400

    verif = Verificacion.query.filter_by(email=email).first()
    if not verif or verif.codigo != codigo:
        return jsonify({"success": False, "error": "Código incorrecto"}), 400


    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({"success": False, "error": "Usuario ya verificado"}), 400

    nuevo_usuario = Usuario(
        nombre=verif.nombre,
        email=verif.email,
        contraseña=verif.contra_codificada,
        rango=verif.rango
    )
    db.session.add(nuevo_usuario)
    db.session.delete(verif)
    db.session.commit()

    login_user(nuevo_usuario)

    return jsonify({"success": True, "mensaje": "Cuenta verificada y sesión iniciada"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("Email")
    contraseña = data.get("Contraseña")

    if not (email and contraseña):
        return jsonify({"success": False, "error": "Faltan campos"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not check_password_hash(usuario.contraseña, contraseña):
        return jsonify({"success": False, "error": "Contraseña incorrecta"}), 401

    login_user(usuario)
    return jsonify({"success": True, "usuario": {
        "Nombre": usuario.nombre,
        "Email": usuario.email
    }}), 200

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("Index"))


def enviar_email(destino, codigo):
    asunto = "Código de verificacion RenaultCup"
    cuerpo = f"Hola,\n\nTu codigo de verificacion es {codigo}"

    mensaje = MIMEMultipart()
    mensaje['From'] = GMAIL_USER
    mensaje['To'] = destino
    mensaje['Subject'] = Header(asunto, 'utf-8')  

    cuerpo_mime = MIMEText(cuerpo, 'plain', 'utf-8')
    mensaje.attach(cuerpo_mime)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        
        texto_email = mensaje.as_string()

        server.sendmail(GMAIL_USER, destino, texto_email)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


@app.route("/")
def Index():
    return render_template('Index.html')

if __name__ == "__main__":
    app.run(debug=True)