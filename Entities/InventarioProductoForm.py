
from wtforms import Form
from wtforms import StringField, SelectMultipleField, RadioField, EmailField, IntegerField, DecimalField, widgets, SelectFieldBase, SelectField
from wtforms import validators

class InventarioProductoForm (Form):


    nombreProducto = StringField("Nombre del Producto", [validators.DataRequired(message='Debes ingresar el nombre del producto'),
                                    validators.length(min=1, max=100, message= 'El nombre del producto debe tener de 1 a 100 caracteres')]) 
    
    alias = StringField("Alias del Producto", [validators.DataRequired(message='Debes ingresar el alias del producto'),
                                    validators.length(min=1, max=50, message= 'El alias del producto debe tener de 1 a 50 caracteres')])

    diasCaducidad = IntegerField("Dias de Caducidad", [validators.DataRequired(message= 'Debes ingresar los dias de caducidad'),
                                        validators.number_range(min=1, message='El producto debe tener al menos 1 dia de caducidad')]) 
    
    costoProducto = DecimalField("Costo del Producto", [validators.DataRequired(message= 'Debes ingresar el costo del producto'),
                                        validators.number_range(min=1, message='El producto debe tener un costo mayor a 0')]) 

    materiales = SelectField("Ingredientes", coerce=int)