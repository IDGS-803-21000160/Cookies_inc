from wtforms import Form
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, DecimalField, FloatField
from wtforms import validators

class InventarioMerma (Form):

    merma = FloatField("Ingresa la cantidad a enviar a merma", [validators.DataRequired(message= 'Debes ingresar una cantidad'),
                                        validators.number_range(min = 0.0000001, message='Debe ser una cantidad mayor a 0')])
    
    descripcion = StringField("Motivo", [validators.DataRequired(message= 'Debes ingresar un motivo')])

class InventarioSalida (Form):

    cantidad = FloatField("Cantidad", [validators.DataRequired(message= 'Debes ingresar una cantidad'),
                                        validators.number_range(min = 0.0000001, message='Debe ser una cantidad mayor a 0')])
    
    descripcion = StringField("Motivo", [validators.DataRequired(message= 'Debes ingresar un motivo')])