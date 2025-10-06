from flask import Flask, redirect,url_for
from flask_cors import CORS
from flask_login import  login_required, logout_user


from py.Rutas import rutas
from py.apis import apis
from py.db import db
from py.LyS import SyL,login_manager


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/cobro_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'

db.init_app(app)

app.register_blueprint(rutas)
app.register_blueprint(apis)
app.register_blueprint(SyL)

login_manager.init_app(app)
login_manager.login_view = "login"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("Index"))


if __name__ == "__main__":
    app.run(debug=True)