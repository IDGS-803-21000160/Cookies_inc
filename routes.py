from flask import Flask
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text, create_engine

#Impiortacion del modelo de formulario de material

from Entities.Inventario import db
from datetime import datetime
from Routes.Inventario.InventarioRoute import modulo_inventario
from Routes.Produccion.ProducionRoute import modulo_produccion
from Routes.Dashboard.DashboardRoutes import modulo_dashboard
from flask_mysqldb import MySQL
from config import DevelopmentConfig

app = Flask(__name__)
csrf=CSRFProtect()
mysql = MySQL(app)
# csrf=CSRFProtect()
app.config.from_object(DevelopmentConfig)

app.register_blueprint(modulo_inventario)
# app.register_blueprint(modulo_produccion)
# app.register_blueprint(modulo_dashboard)


if __name__ == "__main__":
    db.init_app(app)
    mysql.init_app(app)
    csrf.init_app(app)
    with app.app_context():
         db.create_all()
    app.run(port=5000, host='0.0.0.0', debug=True)    