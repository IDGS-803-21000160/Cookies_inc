from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, current_app

modulo_produccion = Blueprint('modulo_produccion', __name__)
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# ''''''''''''''''''''''''''PRODUCCION'''''''''''''''''''''''''''''''''''''''

@modulo_produccion.route('/produccion')
def produccion():
    productos = getProductos()
    return render_template("Produccion/produccion.html", productos=productos)

def getProductos():
    query = """
    select inv.id_inventario as idInv, p.id_producto as idPro, p.nombre_producto as nombre, inv.cantidad_inv as cantidad
    from inventario inv join producto p on inv.producto_inv = p.id_producto 
    where p.id_producto not in 
        (select pi.productoid_itm from produccionitem pi join produccion p ON p.id_produccionitem = pi.id_produccionitem where p.fecha_fin is null);
    """
    # Ejecutar la consulta
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

@modulo_produccion.route('/agregarProduccion', methods=['GET'])
def agregarProduccion():
    idProducto = int(request.args.get('idProducto'))

    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.callproc('agregarProduccion', (idProducto,))
    # cur.execute("CALL agregarProduccion(%s)", (idProducto))
    current_app.mysql.connection.commit()
    cur.close()
    return {'response':'success'}

@modulo_produccion.route('/produccionGalleta', methods=['GET'])
def produccionGalleta():
    query = """
    SELECT 
        pi.id_produccionitem as idProduccionitem, prod.id_producto as idProducto, prod.nombre_producto as nombre,
        GROUP_CONCAT(m.nombre_mat SEPARATOR ' | ') AS materiales, min(floor(inv.cantidad_inv/ri.cantidad)) as cuantas
    FROM 
        produccionitem pi
        JOIN produccion p ON p.id_produccionitem = pi.id_produccionitem
        JOIN producto prod ON prod.id_producto = pi.productoid_itm
        JOIN recetaitem ri ON ri.productoid_itm = prod.id_producto
        JOIN material m ON m.id_material = ri.materialid_itm
        join inventario inv on inv.material_inv = m.id_material
    where p.fecha_fin is null
    GROUP BY 
        pi.id_produccionitem;
    """
    # Ejecutar la consulta
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    data = cur.fetchall()
    cur.close()

    return render_template("Produccion/producirGalleta.html", recetas = data)


@modulo_produccion.route('/descontarProduccion', methods=['GET'])
def descontarProduccion():

    idProducto = request.args.get('idProducto')
    cantidad = request.args.get('cantidad')
    idProduccionitem = request.args.get('idProduccionitem')
    #print('producto: ', idProducto, ' cantidad: ', cantidad, ' produccionitem: ', idProduccionitem)
    # Preparar el nombre del procedimiento almacenado y los parámetros

    # Llamar al procedimiento almacenado
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.callproc('descontarProduccion', (idProducto, cantidad,idProduccionitem))
    current_app.mysql.connection.commit()
    # Obtener los resultados del procedimiento almacenado
    cur.close()
    return {'response':'success'}