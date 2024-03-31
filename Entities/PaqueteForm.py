
from wtforms import Form
from wtforms import StringField, SelectMultipleField, RadioField, EmailField, IntegerField, DecimalField, widgets, SelectFieldBase, SelectField
from wtforms import validators

class PaqueteForm (Form):


    nombrePaquete = StringField("Nombre del Paquete", [validators.DataRequired(message='Debes ingresar el nombre del paquete'),
                                    validators.length(min=1, max=100, message= 'El nombre del paquete debe tener de 1 a 100 caracteres')]) 
    
    costoPaquete = DecimalField("Costo del Paquete", [validators.DataRequired(message= 'Debes ingresar el costo del paquete'),
                                        validators.number_range(min=1, message='El paquete debe tener un costo mayor a 0')]) 

    productos = SelectField("Productos", coerce=int)