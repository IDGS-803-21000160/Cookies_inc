
from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # Importar desde flask_sqlalchemy
from datetime import datetime
from sqlalchemy import Boolean

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Puedes cambiar la URI según tu base de datos
db = SQLAlchemy(app)

class Inventario(db.Model):
    __tablename__ = 'inventario'
    id_inventario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipostock_inv = db.Column(db.Integer)
    producto_inv = db.Column(db.Integer)
    material_inv = db.Column(db.Integer)
    tipo_inv = db.Column(db.Integer)
    cantidad_inv = db.Column(db.Double)
    fecha_caducidad = db.Column(db.DateTime)
    estatus = db.Column(Boolean, default=1)
    usuario_registro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)  # Corregir el tipo de columna

class Material(db.Model):
    __tablename__ = 'material'
    id_material = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_mat = db.Column(db.String(100), nullable=False)
    dias_caducidad = db.Column(db.Integer, nullable=False)
    unidad_medida = db.Column(db.String(10), nullable=False)
    costo_mat = db.Column(db.Float, nullable=False)
    estatus = db.Column(Boolean, default=1)
    usuario_registro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)

class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_producto = db.Column(db.String(100), nullable=False)
    alias = db.Column(db.String(100), nullable=False)
    estatus = db.Column(Boolean, default=1)
    usuario_registro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    costoproducto = db.Column(db.Float, nullable=False)
    dias_caducidadpd= db.Column(db.Integer, nullable=False)

class RecetaItem(db.Model):
    __tablename__ = 'recetaitem'
    id_recetaitem = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productoid_itm = db.Column(db.Integer, nullable=False)
    materialid_itm = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    estatus = db.Column(Boolean, default=1)
    usuario_registro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)

class TipoStock(db.Model):
    __tablename__ = 'tipostock'
    id_tipostock = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_stock = db.Column(db.String(100), nullable=False)
    estatus = db.Column(Boolean, default=1)
    usuario_registro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)

class TipoInventario(db.Model):
    __tablename__ = 'tipoinventario'
    id_tipoInventario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_tipoInv = db.Column(db.String(100), nullable=False)
    estatus = db.Column(Boolean, default=1)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)

class Paquete(db.Model):
    __tablename__ = 'paquete'
    id_paquete = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_paq = db.Column(db.String(100), nullable=False)
    costopaquete_paq = db.Column(db.Float, nullable=False)
    cantidadproductos_paq = db.Column(db.Integer, nullable=False)
    estatus = db.Column(Boolean, default=1)
    usuarioregistro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)

class PaqueteItem(db.Model):
    __tablename__ = 'paqueteitem'
    id_paqueteitem = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paqueteid_itm = db.Column(db.Integer, nullable=False)
    productoid_itm = db.Column(db.Integer, nullable=False)
    cantidadproducto_itm = db.Column(db.Float, nullable=False)
    estatus = db.Column(Boolean, default=1)
    usuarioregistro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)