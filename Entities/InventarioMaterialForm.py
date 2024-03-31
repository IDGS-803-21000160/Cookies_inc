
from wtforms import Form
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, DecimalField
from wtforms import validators

class InventarioMaterialForm (Form):


    nombreMaterial = StringField("Nombre del Material", [validators.DataRequired(message='Debes ingresar el nombre del material'),
                                    validators.length(min=1, max=100, message= 'El nombre del material debe tener de 1 a 100 caracteres')]) 
    
    diasCaducidad = IntegerField("Dias de Caducidad", [validators.DataRequired(message= 'Debes ingresar los dias de caducidad'),
                                        validators.number_range(min=1, message='El material debe tener al menos 1 dia de caducidad')]) 

    unidadMedidaAgregar = SelectField("Unidad de Medida", choices=[('Kg', 'Kg'), ('Litro', 'Litro'), ('pieza', 'pieza')]) 
    
    costoMaterial = DecimalField("Costo del Material", [validators.DataRequired(message= 'Debes ingresar el costo del material'),
                                        validators.number_range(min=0.0001, message='El material debe tener un costo mayor a 0')]) 
