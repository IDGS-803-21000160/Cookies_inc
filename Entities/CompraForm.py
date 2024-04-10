from wtforms import Form
from wtforms import SelectField, IntegerField, StringField
from wtforms.validators import NumberRange

class CompraForm (Form):

    tipo_prov = SelectField("Selecciona un Proveedor", coerce=int, render_kw={"class": "input-container"})
    
    cantidad_producto_1 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_2 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_3 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_4 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_5 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_6 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_7 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_8 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_9 =   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_10 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_11 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_12=   IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_13 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_14 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_15 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_16 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_17 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_18 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_19 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_20 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_21 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_22 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_23 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_24 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_25 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_26 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_27 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_28 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_29 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_30 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_31 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_32 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_33 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_34 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_35 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_36 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_37 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_38 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    cantidad_producto_39 =  IntegerField('Cantidad', default=0, render_kw={"class": "input-container"}, validators=[NumberRange(min=0)])
    
    def limpiar_campos(self):
        for i in range(1, 36):  # Itera sobre los campos de cantidad_producto_1 a cantidad_producto_35
            setattr(self, f'cantidad_producto_{i}', 0)