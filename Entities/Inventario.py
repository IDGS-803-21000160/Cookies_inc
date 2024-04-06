
from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # Importar desde flask_sqlalchemy
from datetime import datetime
from sqlalchemy import Boolean
from flask_login import UserMixin

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
    cantidad_merma = db.Column(db.Float, nullable=False)

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


class Usuario(db.Model,UserMixin):
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True)  # Auto increment se maneja automáticamente
    tipousuario = db.Column(db.String(50), nullable=False)
    nombrecompleto = db.Column(db.String(70), nullable=False)
    estatus = db.Column(db.String(1), default='1')  # BIT en MySQL se maneja como Boolean en SQLAlchemy
    usuario_registro = db.Column(db.Integer, nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.now)
    ultima_sesion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    ultima_modificacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)

    def get_id(self):
        return str(self.id_usuario)

class LoginLog(db.Model):
    __tablename__ = 'login_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    id_us = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    user = db.Column(db.String(100))
    login_time = db.Column(db.DateTime, default=datetime.now)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    login_successful = db.Column(db.Boolean, default=True)
    
# ************** COMPRA *************** 
class Compra(db.Model):
    __tablename__ = 'compra'

    id_compra = db.Column(db.Integer, primary_key=True)
    proveedorid_comp = db.Column(db.Integer, db.ForeignKey('proveedor.id_proveedor'))
    usuario_comp = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    folio_comp = db.Column(db.String(50))
    fecha_comp = db.Column(db.DateTime)
    fecha_cancelacion = db.Column(db.DateTime)
    cantidad = db.Column(db.Integer)
    total = db.Column(db.Float)
    estatus = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime)

    proveedor = db.relationship('Proveedor', backref='compras')
    usuario = db.relationship('Usuario', backref='compras')
    
class CompraItem(db.Model):
    __tablename__ = 'compraitem'

    id_compraitem = db.Column(db.Integer, primary_key=True)
    compra_itm = db.Column(db.Integer, db.ForeignKey('compra.id_compra'))
    materialid_itm = db.Column(db.Integer, db.ForeignKey('material.id_material'))
    cantidad = db.Column(db.Integer)
    subtotal = db.Column(db.Float)
    estatus = db.Column(db.Integer)
    usuario_registro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime)
    
    compra = db.relationship('Compra', backref='compraitems')
    material = db.relationship('Material', backref='compraitems')
    
class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    id_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(20))
    dias_visita = db.Column(db.String(50))
    estatus = db.Column(Boolean, nullable=False, default=True)
    usuario_registro = db.Column(db.Integer)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)