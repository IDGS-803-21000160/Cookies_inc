from wtforms import Form
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, DecimalField, FloatField
from wtforms import validators

class InventarioMerma (Form):

    merma = FloatField("Ingresa la cantidad a enviar a merma", [validators.DataRequired(message= 'Debes ingresar una cantidad'),
                                        validators.number_range(min=1, message='Debe ser una cantidad mayor a 0')])

class InventarioSalida (Form):

    cantidad = IntegerField("Cantidad", [validators.DataRequired(message= 'Debes ingresar una cantidad'),
                                        validators.number_range(min=1, message='Debe ser una cantidad mayor a 0')])