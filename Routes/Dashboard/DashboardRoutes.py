from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Flask
from Entities.Inventario import db
from config import DevelopmentConfig
from flask_wtf.csrf import CSRFProtect
import datetime

modulo_dashboard = Blueprint('modulo_dashboard', __name__)
csrf=CSRFProtect()
# ''''''''''''''''''''''''''DASHBOARD'''''''''''''''''''''''''''''''''''''''
@modulo_dashboard.route('/dashboard')
def dashboard():    
    ventas = getVentasAnio()
    produccion = getProduccion()
    caducidadesINV = getCaducidades()
    cardData = getCards()


    for item in cardData:
        caducidades = item['Caducidades']
        cantidadVentas = item['cantidadVentas']
        totalVentas = item['totalVentas']
        productoVendido = item['productoVendido']

    return render_template("Dashboard/dashboard.html",produccion=produccion, ventas = ventas, caducidadesINV=caducidadesINV,productoVendido=productoVendido, caducidades=caducidades, cantidadVentas = cantidadVentas, totalVentas=totalVentas)

@modulo_dashboard.route('/get_ventasPr', methods=['GET'])
def get_ventasPr():
    # Get the week number from the request parameters
    week_number = request.args.get('week_number')

    # Prepare the SQL query to filter by week and sum quantities
    query = """
        SELECT paquete.nombre_paq as nombre, sum(ventaitem.cantidad) as cantidad, month(ventaitem.fecha_registro) as mes 
	    FROM ventaitem
        JOIN venta ON venta.id_venta = ventaitem.ventaid_itm
        join paquete on ventaitem.paqueteid_itm = paquete.id_paquete
        WHERE month(ventaitem.fecha_registro) = %s
        GROUP BY venta.fecha_venta, paquete.nombre_paq;
    """

    # Execute the query with the week number parameter
    cur = current_app.current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query, (week_number,))
    data = cur.fetchall()
    cur.close()

    return current_app.jsonify(data)

@modulo_dashboard.route('/getVentasAnio', methods=['GET'])
def getVentasAnio():
    query = """
        SELECT sum(ventaitem.cantidad) as cantidad, month(ventaitem.fecha_registro) as mes
        FROM ventaitem
        GROUP BY month(ventaitem.fecha_registro);
    """
    # Ejecutar la consulta
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    data = cur.fetchall()
    cur.close()

    return current_app.jsonify(data)

def getVentasAnio():
    query = """
        SELECT cliente_venta AS Cliente_ID,
            folio_venta AS Folio_Venta,
            fecha_venta AS Fecha_Venta,
            id_venta AS Id_Venta,
            total_ventas AS Total_Venta
        FROM venta
        ORDER BY fecha_registro DESC
        LIMIT 6;
    """
    # Ejecutar la consulta
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

def getCaducidades():
    query = """
    SELECT 
    inv.fecha_caducidad AS caducidadInventario,
    COALESCE(p.nombre_producto, m.nombre_mat) AS nombre,
    inv.id_inventario AS idInventario
    FROM 
    inventario inv 
    left JOIN 
    material m ON inv.material_inv = m.id_material 
    left JOIN 
    producto p ON inv.producto_inv = p.id_producto
    ORDER BY inv.fecha_caducidad ASC limit 6;
    """
    # Ejecutar la consulta
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

def getCards():
    data = []

    query = """ SELECT COUNT(*) AS cuenta FROM inventario WHERE DATEDIFF(fecha_caducidad, CURDATE()) <= 20;"""
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    caducidades = cur.fetchone()

    query = """ SELECT count(*) as cantidadVentas FROM venta; """
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    cantidadVentas = cur.fetchone()

    query = """ SELECT sum(total_ventas) as totalVentas FROM venta; """
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    totalVentas = cur.fetchone()
    cur.close()

    query = """SELECT p.nombre_paq AS productoVendido, COUNT(vi.id_ventaitem) AS cantidad_ventas 
    FROM ventaitem vi 
    JOIN paqueteitem pi ON vi.paqueteid_itm = pi.id_paqueteitem
    join paquete p on p.id_paquete = pi.paqueteid_itm
    GROUP BY p.nombre_paq
    ORDER BY cantidad_ventas DESC LIMIT 1; """
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    productoVendido = cur.fetchone()
    cur.close()

    # Append the results to the data list
    data.append({
        "Caducidades": caducidades['cuenta'],
        "cantidadVentas": cantidadVentas['cantidadVentas'],
        "totalVentas": totalVentas['totalVentas'],
        "productoVendido": productoVendido['productoVendido']

    })

    return data

def getProduccion():
    query = """  SELECT prod.nombre_producto as nombre, pi.costo as costo, pi.costo as costo, p.fecha_inicio as fechaInicio, coalesce(p.fecha_fin, 'En espera') as fechaFin, 
    CASE 
        WHEN p.fecha_fin IS NULL THEN 0 
        ELSE 1 
    END AS estado_fecha
    FROM produccion p JOIN produccionitem pi ON p.id_produccionitem = pi.id_produccionitem
    join producto prod on prod.id_producto = pi.productoid_itm
    WHERE p.fecha_inicio IS NOT NULL order by  p.fecha_inicio asc limit 6;"""
    # Ejecutar la consulta
    cur = current_app.mysql.connection.cursor(current_app.MySQLdb.cursors.DictCursor)
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data