from wtforms import Form
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, DecimalField, FloatField
from wtforms import validators

class InventarioForm (Form):

    tipo_inv = SelectField("Tipo de Inventario", coerce=int)
    material = SelectField("Material", coerce=int)
    producto = SelectField("Producto", coerce=int)

    cantidad = IntegerField("Cantidad", [validators.DataRequired(message= 'Debes ingresar una cantidad'),
                                        validators.number_range(min=1, message='Debe ser una cantidad mayor a 0')])
    
    merma = FloatField("Ingresa la cantidad a enviar a merma", [validators.DataRequired(message= 'Debes ingresar una cantidad'),
                                        validators.number_range(min=1, message='Debe ser una cantidad mayor a 0')])
    