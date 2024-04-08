from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import text
from Entities.Inventario import db


modulo_produccion = Blueprint('modulo_produccion', __name__)
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# ''''''''''''''''''''''''''PRODUCCION'''''''''''''''''''''''''''''''''''''''

@modulo_produccion.route('/produccion', methods=['GET','POST'])
def produccion():
    if request.method == 'POST':
        idPro = request.form.get('idPro')  # Obtener el idPro enviado en la solicitud POST
        agregarProduccion(idPro)
    
    productos = getProductos()
    return render_template("Produccion/produccion.html", productos=productos)

def getProductos():
    query = """
    select min(inv.id_inventario) as idInv, p.id_producto as idPro, min(p.nombre_producto) as nombre, sum(inv.cantidad_inv) as cantidad
    from inventario inv join producto p on inv.producto_inv = p.id_producto 
    where p.id_producto not in 
        (select pi.productoid_itm from produccionitem pi join produccion p ON p.id_produccionitem = pi.id_produccionitem where p.fecha_fin is null)
        and inv.tipostock_inv = 1
	group by p.id_producto;
    """
    # Ejecutar la consulta
    data = db.session.execute(text(query))
    return data

def agregarProduccion(idProducto):
    db.session.execute(
        text("CALL agregarProduccion(:idProducto)"),
        {"idProducto": idProducto}
    )
    db.session.commit()
    return {'response':'success'}

@modulo_produccion.route('/produccionGalleta', methods=['GET','POST'])
def produccionGalleta():
    if request.method == 'POST':
        idProducto = request.form.get('idProducto')
        counter = str(request.form.get('counter'))
        cantidad = request.form.get('cuantas_'+counter)
        idProduccionitem = request.form.get('idProduccionitem')

        # print('idp: ', idProducto,'counter: ',counter,'cant: ',cantidad, 'idpi: ', idProduccionitem)
        descontarProduccion(idProducto,cantidad,idProduccionitem)
    
    query = """
        SELECT 
            pi.id_produccionitem as idProduccionitem, prod.id_producto as idProducto, min(prod.nombre_producto) as nombre,
            GROUP_CONCAT(DISTINCT m.nombre_mat SEPARATOR ' | ') AS materiales , min(sum.cuantas) as cuantas
        FROM 
            produccionitem pi
            JOIN produccion p ON p.id_produccionitem = pi.id_produccionitem
            JOIN producto prod ON prod.id_producto = pi.productoid_itm
            JOIN recetaitem ri ON ri.productoid_itm = prod.id_producto
            JOIN material m ON m.id_material = ri.materialid_itm
            join (select p.id_producto as idProducto, inv.material_inv as idMaterial, sum(inv.cantidad_inv) as matExistente , min(ri.cantidad) as matNecesitado,
                floor(sum(inv.cantidad_inv)/min(ri.cantidad)) as cuantas
                from recetaitem ri 
                join material m on m.id_material = ri.materialid_itm
                join inventario inv on inv.material_inv = m.id_material
                join producto p on ri.productoid_itm = p.id_producto
                where inv.tipostock_inv = 1
                group by inv.material_inv, p.id_producto) sum ON sum.idProducto= pi.productoid_itm
        where p.fecha_fin is null
        GROUP BY 
            pi.id_produccionitem;
        """
    # Ejecutar la consulta
    data = db.session.execute(text(query))

    return render_template("Produccion/producirGalleta.html", recetas = data)


def descontarProduccion(idProducto,cantidad,idProduccionitem):
    #print('producto: ', idProducto, ' cantidad: ', cantidad, ' produccionitem: ', idProduccionitem)
    # Preparar el nombre del procedimiento almacenado y los parámetros

    # Llamar al procedimiento almacenado

    db.session.execute(
        text("CALL descontarProduccion(:idProducto, :cantidad, :idProduccionitem)"),
        {"idProducto": idProducto, "cantidad":cantidad, "idProduccionitem":idProduccionitem}
    )
    db.session.commit()
    return {'response':'success'}