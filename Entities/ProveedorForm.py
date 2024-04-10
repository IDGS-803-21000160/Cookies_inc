
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators,ValidationError,IntegerField,DateTimeLocalField,SelectField,BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional,Regexp,Email
import re
import bleach


class ProveedorFormReg(FlaskForm):
    id_proveedor = IntegerField('ID Proveedor')
    nombre = StringField('Nombre del proveedor', validators=[DataRequired(message='El campo es requerido'), Length(max=50)])
    telefono = IntegerField('Teléfono',validators=[DataRequired(message='El campo es requerido')] )
    correo = StringField('Correo', validators=[Email(message='Correo inválido'), Length(max=50)])
    dias_visita = StringField('Días de Visita', validators=[DataRequired(message='El campo es requerido'), Length(max=50)])
    estatus = IntegerField('Estatus') 
    usuario_registro = IntegerField('Usuario Registro', validators=[Optional()])
    fecha_registro = DateTimeLocalField('Fecha de Registro')
    lunes=BooleanField('Lunes')
    martes=BooleanField('Martes')
    miercoles=BooleanField('Miercoles')
    jueves=BooleanField('Jueves')
    viernes=BooleanField('Viernes')