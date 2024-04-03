from flask import Blueprint, render_template, request, redirect, url_for, flash, current_modulo_dashboard, Flask
from Entities.Inventario import db
from sqlalchemy import text
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

    #----- CHARTS ------
    ventasAnio = getVentasAnio2()
    ventasPr = get_ventasPr()

    return render_template("Dashboard/dashboard.html",ventasPr=ventasPr, ventasAnio=ventasAnio,produccion=produccion, ventas = ventas, caducidadesINV=caducidadesINV,productoVendido=productoVendido, caducidades=caducidades, cantidadVentas = cantidadVentas, totalVentas=totalVentas)

def get_ventasPr():

    # Prepare the SQL query to filter by week and sum quantities
    query = text("""
        SELECT paquete.nombre_paq as nombre, sum(ventaitem.cantidad) as cantidad, month(venta.fecha_venta) as mes 
	    FROM ventaitem
        JOIN venta ON venta.id_venta = ventaitem.ventaid_itm
        join paquete on ventaitem.paqueteid_itm = paquete.id_paquete
        GROUP BY month(venta.fecha_venta), paquete.nombre_paq;
    """)

    # Execute the query with the week number parameter

    data = db.session.execute(query)

    # Estructura para almacenar los resultados por mes
    resultados_por_mes = {}

    # Iterar sobre los resultados y almacenarlos en la estructura
    for row in data:
        mes = row['mes']
        if mes not in resultados_por_mes:
            resultados_por_mes[mes] = []
        resultados_por_mes[mes].modulo_dashboardend(row)

    return resultados_por_mes

def getVentasAnio2():
    query = text("""
        SELECT COALESCE(SUM(ventaitem.cantidad), 0) AS cantidad, months.mes
        FROM (
            SELECT 1 AS mes
            UNION SELECT 2 AS mes
            UNION SELECT 3 AS mes
            UNION SELECT 4 AS mes
            UNION SELECT 5 AS mes
            UNION SELECT 6 AS mes
            UNION SELECT 7 AS mes
            UNION SELECT 8 AS mes
            UNION SELECT 9 AS mes
            UNION SELECT 10 AS mes
            UNION SELECT 11 AS mes
            UNION SELECT 12 AS mes
        ) AS months
        LEFT JOIN ventaitem ON MONTH(ventaitem.fecha_registro) = months.mes
        GROUP BY months.mes;
    """)
    # Ejecutar la consulta

    data = db.session.execute(query)

    # Format the data as list of dictionaries
    formatted_data = [{'cantidad': row['cantidad'], 'mes': row['mes']} for row in data]

    # Return JSON response
    return formatted_data

def getVentasAnio():
    query = text("""
        SELECT cliente_venta AS Cliente_ID,
            folio_venta AS Folio_Venta,
            fecha_venta AS Fecha_Venta,
            id_venta AS Id_Venta,
            total_ventas AS Total_Venta
        FROM venta
        ORDER BY fecha_registro DESC
        LIMIT 6;
    """)
    # Ejecutar la consulta

    data = db.session.execute(query)
    return data

def getCaducidades():
    query = text("""
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
    """)
    # Ejecutar la consulta
    data = db.session.execute(query)

    return data

def getCards():
    data = []

    query = text(""" SELECT COUNT(*) AS cuenta FROM inventario WHERE DATEDIFF(fecha_caducidad, CURDATE()) <= 20;""")
    caducidades = db.execute(query).fetchone()

    query = """ SELECT count(*) as cantidadVentas FROM venta; """
    cantidadVentas = db.execute(text(query)).fetchone()

    query = """ SELECT sum(total_ventas) as totalVentas FROM venta; """
    totalVentas = db.execute(text(query)).fetchone()

    query = """SELECT p.nombre_paq AS productoVendido, COUNT(vi.id_ventaitem) AS cantidad_ventas 
    FROM ventaitem vi 
    JOIN paqueteitem pi ON vi.paqueteid_itm = pi.id_paqueteitem
    join paquete p on p.id_paquete = pi.paqueteid_itm
    GROUP BY p.nombre_paq
    ORDER BY cantidad_ventas DESC LIMIT 1; """

    productoVendido = db.execute(text(query)).fetchone()

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
    data = db.execute(text(query))
    return data
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''