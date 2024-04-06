from flask import Flask,render_template
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text, create_engine

#Impiortacion del modelo de formulario de material

from Entities.Inventario import db,Usuario
from datetime import datetime
from Routes.Inventario.InventarioRoute import modulo_inventario
from Routes.Produccion.ProducionRoute import modulo_produccion
from Routes.Dashboard.DashboardRoutes import modulo_dashboard
from Routes.Login.LoginRoute import modulo_login
from Routes.Usuarios.UsuariosRoute import modulo_usuarios
from Routes.Compra.CompraRoutes import modulo_compras
from flask_mysqldb import MySQL
from config import DevelopmentConfig
from flask_login import LoginManager

app = Flask(__name__)
csrf=CSRFProtect()
mysql = MySQL(app)

login_manager_app=LoginManager(app)


# csrf=CSRFProtect()
app.config.from_object(DevelopmentConfig)
app.register_blueprint(modulo_login)
app.register_blueprint(modulo_usuarios)
app.register_blueprint(modulo_inventario)
app.register_blueprint(modulo_produccion)
app.register_blueprint(modulo_dashboard)
app.register_blueprint(modulo_compras)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('ErrorPage/404.html'),404

@app.errorhandler(400)
def bad_request(e):
    return render_template('ErrorPage/400.html'), 400


@app.errorhandler(401)
def bad_request(e):
    return render_template('ErrorPage/401.html'), 400

@login_manager_app.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


if __name__ == "__main__":
    db.init_app(app)
    mysql.init_app(app)
    csrf.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)    