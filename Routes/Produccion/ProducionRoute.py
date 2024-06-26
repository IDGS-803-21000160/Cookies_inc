from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import text
from Entities.Inventario import db
from permissions import pos_required
from flask_login import login_required,current_user

modulo_produccion = Blueprint('modulo_produccion', __name__)
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# ''''''''''''''''''''''''''PRODUCCION'''''''''''''''''''''''''''''''''''''''

@modulo_produccion.route('/produccion', methods=['GET','POST'])
@pos_required
@login_required
def produccion():
    if request.method == 'POST':
        idPro = request.form.get('idPro')  # Obtener el idPro enviado en la solicitud POST
        counter = request.form.get('counter')
        cantidadInput = 'cuantas_'+counter
        cantidad = request.form.get(cantidadInput)
        agregarProduccion(idPro,cantidad)
    
    productos = getProductos()

    return render_template("Produccion/produccion.html", productos=productos)

def getProductos():
    query = """
    select min(inv.id_inventario) as idInv, p.id_producto as idPro, min(p.nombre_producto) as nombre, sum(inv.cantidad_inv) as cantidad, min(sum.cuantas) as cuantas
    from inventario inv join producto p on inv.producto_inv = p.id_producto
    join (select idProducto, min(cuantas) as cuantas from (select p.id_producto as idProducto, inv.material_inv as idMaterial, sum(inv.cantidad_inv) as matExistente , min(ri.cantidad) as matNecesitado,
			floor(sum(inv.cantidad_inv)/min(ri.cantidad)) as cuantas
			from recetaitem ri 
			join material m on m.id_material = ri.materialid_itm
			join (select * from inventario where tipostock_inv = 1) inv on inv.material_inv = m.id_material
			join producto p on ri.productoid_itm = p.id_producto
			group by inv.material_inv, p.id_producto) agrupacion
			group by idProducto) sum on sum.idProducto = p.id_producto
    where p.id_producto 
		not in (select pi.productoid_itm from produccionitem pi join produccion p ON p.id_produccionitem = pi.id_produccionitem where p.fecha_fin is null) 
    and inv.tipostock_inv = 1 
    group by 2;
    """
    # Ejecutar la consulta
    data = db.session.execute(text(query))
    return data

def agregarProduccion(idProducto,cantidad):
    db.session.execute(
        text("CALL agregarProduccion(:idProducto, :cantidad)"),
        {"idProducto": idProducto,"cantidad": cantidad }
    )
    db.session.commit()
    return {'response':'success'}

@modulo_produccion.route('/produccionGalleta', methods=['GET','POST'])
@login_required
def produccionGalleta():
    if request.method == 'POST':
        acceptacion = request.form.get('idPro')
        idProducto = request.form.get('idProducto')
        counter = str(request.form.get('counter'))
        cantidad = request.form.get('cuantas_'+counter)
        idProduccionitem = request.form.get('idProduccionitem')

        #USER
        usuario_registro=current_user.id_usuario

        # print('idp: ', idProducto,'counter: ',counter,'cant: ',cantidad, 'idpi: ', idProduccionitem)
        if acceptacion == '1':
            print("entro")
            descontarProduccion(idProducto,cantidad,idProduccionitem,usuario_registro)
        else:
            rechazarProduccion(idProducto,cantidad,idProduccionitem,usuario_registro)

    
    query = """
        SELECT 
            pi.id_produccionitem as idProduccionitem, prod.id_producto as idProducto, min(prod.nombre_producto) as nombre,
            GROUP_CONCAT(DISTINCT m.nombre_mat SEPARATOR ' | ') AS materiales , pi.cantidad as cuantas, date(pi.fecha_registro) as fechaSolicitud
        FROM 
            produccionitem pi
            JOIN produccion p ON p.id_produccionitem = pi.id_produccionitem
            JOIN producto prod ON prod.id_producto = pi.productoid_itm
            JOIN recetaitem ri ON ri.productoid_itm = prod.id_producto
            JOIN material m ON m.id_material = ri.materialid_itm
        where p.fecha_fin is null
        GROUP BY 
            pi.id_produccionitem;
        """
    # Ejecutar la consulta
    data = db.session.execute(text(query))
    return render_template("Produccion/producirGalleta.html", recetas = data)


def descontarProduccion(idProducto,cantidad,idProduccionitem,usuario_registro):
    db.session.execute(
        text("CALL descontarProduccion(:idProducto, :cantidad, :idProduccionitem, :usuario_registro)"),
        {"idProducto": idProducto, "cantidad":cantidad, "idProduccionitem":idProduccionitem,"usuario_registro":usuario_registro}
    )
    print(" ",idProducto," ",cantidad," ",idProduccionitem," ",usuario_registro)
    db.session.commit()
    #print("idProduccionitem: ",idProduccionitem)
    return {'response':'success'}

def rechazarProduccion(idProducto,cantidad,idProduccionitem,usuario_registro):
    db.session.execute(
        text("CALL rechazar(:idProducto, :cantidad, :idProduccionitem, :usuario_registro)"),
        {"idProducto": idProducto, "cantidad":cantidad, "idProduccionitem":idProduccionitem,"usuario_registro":usuario_registro}
    )
    db.session.commit()
    return {'response':'success'}