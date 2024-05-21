from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators,ValidationError,IntegerField,DateTimeLocalField,SelectField,BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional,Regexp,Email
import re
import bleach

class ClienteFormReg(FlaskForm):
    nombreCliente = StringField('Nombre del Cliente', validators=[DataRequired(message='El campo es requerido'), Length(max=50)])
    correo = StringField('Correo', validators=[Email(message='Correo inválido'), Length(max=50)])
