from flask import Flask
from flask_cors import CORS


from py.Rutas import rutas
from py.apis import apis
from py.db import db
from py.LyS import SyL,login_manager


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/cobro_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'

access_token = "APP_USR-5796444415198491-100214-0079dab88cf789d8b4614de5bcc470cd-2901193336"
if not access_token:
    raise Exception(
        "MERCADOPAGO_ACCESS_TOKEN no está definido en las variables de entorno."
    )


db.init_app(app)

app.register_blueprint(rutas)
app.register_blueprint(apis)
app.register_blueprint(SyL)

login_manager.init_app(app)
login_manager.login_view = "login"




if __name__ == "__main__":
    app.run(debug=True)