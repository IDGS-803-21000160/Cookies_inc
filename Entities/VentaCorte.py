from wtforms import Form
from wtforms import SelectField
from wtforms.validators import NumberRange

class VentaForm(Form):
    tipo_corte = SelectField("Selecciona un rango a buscar", render_kw={"class": "input-container"}, choices=[
        ('dia_actual', 'Día Actual'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('anual', 'Anual')
    ])