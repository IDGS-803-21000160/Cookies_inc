from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_login import UserMixin


db=SQLAlchemy()

class Usuario(db.Model,UserMixin):
    __tablename__ = 'usuario'

    id_us = db.Column(db.Integer, primary_key=True)  # Auto increment se maneja automáticamente
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
        return str(self.id_us)
    

class Proveedor(db.Model):
    __tablename__ = 'proveedor'

    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=True)
    telefono = db.Column(db.Numeric(13, 0), nullable=True)
    correo = db.Column(db.String(50), nullable=True)
    dias_visita = db.Column(db.String(50), nullable=True)
    db.Column(db.String(1), default='1')   # BIT se maneja como Boolean en SQLAlchemy
    usuario_registro = db.Column(db.Integer, nullable=True)
    fecha_registro = db.Column(db.DateTime, nullable=True, default=datetime.now)

class LoginLog(db.Model):
    __tablename__ = 'login_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    id_us = db.Column(db.Integer, db.ForeignKey('usuario.id_us'))
    user = db.Column(db.String(100))
    login_time = db.Column(db.DateTime, default=datetime.now)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    login_successful = db.Column(db.Boolean, default=True)

class VistaDetalleProducto(db.Model):
    __tablename__ = 'vista_detalle_producto'

    # Asumiendo que nombre_producto puede actuar como una clave única para la vista
    nombre_producto = db.Column(db.String, primary_key=True)
    idProducto = db.Column(db.Integer)
    costo = db.Column(db.Float)
    cantidad = db.Column(db.Integer)
    idInventario = db.Column(db.Integer)
    IdProductoInv = db.Column(db.Integer)