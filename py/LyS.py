from flask import render_template,Blueprint, request, jsonify, redirect, url_for
from collections import namedtuple

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from py.db import db

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

SyL = Blueprint('SyL', __name__,template_folder='templates')

login_manager = LoginManager()

GMAIL_USER = "renaultcup0@gmail.com"
GMAIL_PASS = "ywer mdum zooi zvxm"
email= ""
@login_manager.user_loader
def load_user(email):
    return Usuario.query.get(email)



class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    nombre = db.Column(db.String(40))
    email = db.Column(db.String(40),primary_key=True)
    contraseña = db.Column(db.String(200))
    rango = db.Column(db.String(20))

    def get_id(self):
        return self.email 
    
    def is_active(self):
        return True
    
class Verificacion(db.Model):
    __tablename__ = 'Verificacion'
    email = db.Column(db.String(40))
    codigo = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(40))
    contra_codificada = db.Column(db.String(200))
    rango = db.Column(db.String(20))

class Login(FlaskForm):
    user = StringField('user', validators=[DataRequired()])
    password=StringField('password', validators=[DataRequired()])

class Signup(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    user = StringField('user', validators=[DataRequired()])
    password=StringField('password', validators=[DataRequired()])
                                              
class VC(FlaskForm):
    cod = StringField('codigo', validators=[DataRequired()])

                  

@SyL.context_processor
def inject_user_rango():
    if current_user.is_authenticated:
        return dict(rango=current_user.rango)
    return dict()
    
def verificar_codigo(form):
    global email
    codigo = form.cod.data

    print("\nasdsad ",email)

    verif = Verificacion.query.filter_by(email=email).first()
    if not verif or verif.codigo != codigo:
        return "Código incorrecto"


    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return "Usuario ya verificado"

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
    
    return "True"

@SyL.route("/verificar_codigo", methods=["GET","POST"])
def verificar_codigo_page(email=""):
    form = VC()
    info=""
    if form.validate_on_submit():
        info=verificar_codigo(form)
        if info=="True":
            return redirect(url_for('Index'))
    elif email!="":
        form.user=email
    return render_template('signup and login/vc.html',form=form,info=info)

@SyL.route("/check_email", methods=["POST"])
def check_email():
    data = request.get_json()
    email = data.get("Email")
    if not email:
        return jsonify({"exists": False})

    existe = Usuario.query.filter_by(email=email).first() is not None or Verificacion.query.filter_by(email=email).first() is not None
    return jsonify({"exists": existe})

def signup(form):

    nombre = form.name.data
    email = form.user.data
    contraseña = form.password.data
    rango = "c"

    usuario = Usuario.query.filter_by(email=email).first()
    if not (nombre and email and contraseña):
        return "Faltan datos"

    if usuario:
        if not usuario or not check_password_hash(usuario.contraseña, contraseña):
            return "El email ya está registrado y contraseña incorrecta"
        login_user(usuario)
        return "Log"
    verificacion=Verificacion.query.filter_by(email=email).first()
    if verificacion:
        db.session.delete(verificacion)
    contra_codificada = generate_password_hash(contraseña)
    codigo = ''.join(random.choices('0123456789', k=6))

    verif = Verificacion(email=email, codigo=codigo, nombre=nombre, contra_codificada=contra_codificada, rango=rango)
    db.session.add(verif)
    db.session.commit()

    enviado = enviar_email(email, codigo)
    if not enviado:
        return "No se pudo enviar el codigo de verificacion"

    return "True" 

@SyL.route("/signup", methods=["GET","POST"])
def signup_page():
    info=""
    form = Signup()
    if form.validate_on_submit():
        info=signup(form)
        if info=="True":
            global email
            email = form.user.data
            return redirect('/verificar_codigo')
        if info=="Log":
            return redirect(url_for('Index'))
        
    return render_template('signup and login/signup.html',form=form,info=info)

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

def login(form):
    email = form.user.data
    contraseña = form.password.data
    if not (email and contraseña):
        return "Faltan campos"
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario==None:
        return "Contraseña o Email incorrecta/o"
    if not check_password_hash(usuario.contraseña, contraseña):
        return "Contraseña o Email incorrecta/o"
        

    login_user(usuario)
    return True

@SyL.route("/login", methods=['GET', 'POST'])
def login_url():
    form = Login()
    info=""
    if form.validate_on_submit():
        info=login(form)
        if info==True:
            return redirect(url_for('Index'))

    return render_template('signup and login/login.html',form=form,info=info)

