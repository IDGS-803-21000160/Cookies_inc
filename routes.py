from flask import Flask,render_template,flash,redirect,url_for
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text, create_engine
from flask_cors import CORS, cross_origin


#Impiortacion del modelo de formulario de material

from Entities.Inventario import db,Usuario
from datetime import datetime
from Routes.Inventario.InventarioRoute import modulo_inventario
from Routes.Paquetes.PaquetesRoute import modulo_paquetes
from Routes.Materiales.MaterialesRoute import modulo_materiales
from Routes.Productos.ProductosRoute import modulo_producto

from Routes.Produccion.ProducionRoute import modulo_produccion
from Routes.Dashboard.DashboardRoutes import modulo_dashboard
from Routes.Proveedores.ProveedoresRoute import moodulo_proveedor
from Routes.Login.LoginRoute import modulo_login
from Routes.Usuarios.UsuariosRoute import modulo_usuarios
from Routes.Compra.CompraRoutes import modulo_compras
from Routes.Ventas.VentasRoute import modulo_ventas
from flask_mysqldb import MySQL
from config import DevelopmentConfig
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from functools import wraps


app = Flask(__name__)
csrf=CSRFProtect()
mysql = MySQL(app)

login_manager_app=LoginManager(app)

# DESBLOQUEAR CIERTOS ORIGENES
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5000"]}})
#CORS(app, resources={r"/*": {"origins": ["http://192.168.111.246.*", "http://192.168.111.86:8080","http://192.168.111.127.*"]}})



app.config.from_object(DevelopmentConfig)
app.register_blueprint(modulo_login)
app.register_blueprint(modulo_usuarios)
app.register_blueprint(modulo_inventario)
app.register_blueprint(moodulo_proveedor)
app.register_blueprint(modulo_ventas)
app.register_blueprint(modulo_produccion)
app.register_blueprint(modulo_dashboard)
app.register_blueprint(modulo_compras)
app.register_blueprint(modulo_paquetes)
app.register_blueprint(modulo_materiales)
app.register_blueprint(modulo_producto)

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
    return db.session.query(Usuario).get(int(user_id))



if __name__ == "__main__":
    db.init_app(app)
    mysql.init_app(app)
    csrf.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)    