from flask import  render_template, request, redirect, url_for, flash, current_app, Blueprint
from sqlalchemy import text
from Entities.Inventario import db
from sqlalchemy import text
from flask_wtf.csrf import CSRFProtect

modulo_dashboard = Blueprint('modulo_dashboard', __name__)
csrf=CSRFProtect()
# ''''''''''''''''''''''''''DASHBOARD'''''''''''''''''''''''''''''''''''''''
@modulo_dashboard.route('/dashboard')
def dashboard():    
    ventas = getVentasAnio()
    produccion = getProduccion()
    caducidadesINV = getCaducidades()
    cardData = getCards()
    profeCardData = getProfeCards()

    for item in cardData:
        caducidades = item['Caducidades']
        cantidadVentas = item['cantidadVentas']
        totalVentas = item['totalVentas']
        productoVendido = item['productoVendido']

    #CONSULTAS DEL PROFE DE BD IASHNDIOAHSIUFJHOAISDJFIADJSIOFJDS
    for item in profeCardData:
        utilidadGalleta = item['utilidadGalleta']
        paqueteVendido = item['paqueteVendido']
        galletaMerma = item['galletaMerma']

    profe = getProveedoresResponsables()
    costoProduccion = getCostoProduccion()

    #----- CHARTS ------
    ventasAnio = getVentasAnio2()
    ventasPr = get_ventasPr()
    print(ventasPr)

    return render_template("Dashboard/dashboard.html",profe=profe,costoProduccion=costoProduccion,paqueteVendido=paqueteVendido,galletaMerma=galletaMerma,utilidadGalleta=utilidadGalleta, ventasPr=ventasPr, ventasAnio=ventasAnio,produccion=produccion, ventas = ventas, caducidadesINV=caducidadesINV,productoVendido=productoVendido, caducidades=caducidades, cantidadVentas = cantidadVentas, totalVentas=totalVentas)

def get_ventasPr():
    # Prepare the SQL query to filter by week and sum quantities
    query = """
        SELECT paquete.nombre_paq as nombre, sum(ventaitem.cantidad) as cantidad, month(venta.fecha_venta) as mes 
        FROM ventaitem
        JOIN venta ON venta.id_venta = ventaitem.ventaid_itm
        join paquete on ventaitem.paqueteid_itm = paquete.id_paquete
        GROUP BY month(venta.fecha_venta), paquete.nombre_paq;
    """

    # Execute the query with the week number parameter
    data = db.session.execute(text(query))

    # Estructura para almacenar los resultados por mes
    resultados_por_mes = {}

    meses_espanol = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]

    # Iterar sobre los resultados y almacenarlos en la estructura
    for row in data:
        nombre = row[0]
        cantidad = row[1]
        mes_numero = row[2]
        mes_nombre = meses_espanol[mes_numero - 1]
        # Crea un diccionario para cada fila
        row_dict = {'nombre': nombre, 'cantidad': cantidad, 'mes': mes_nombre}
        # Append el diccionario a la lista correspondiente del mes
        if mes_nombre not in resultados_por_mes:
            resultados_por_mes[mes_nombre] = []
        resultados_por_mes[mes_nombre].append(row_dict)

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
    formatted_data = [{'cantidad': row.cantidad, 'mes': row.mes} for row in data]
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
    WHERE inv.fecha_caducidad > CURDATE()
    ORDER BY inv.fecha_caducidad ASC limit 6;
    """)
    # Ejecutar la consulta
    data = db.session.execute(query)

    return data

def getCards():
    data = []

    query = text(""" SELECT COUNT(*) AS cuenta FROM inventario WHERE DATEDIFF(fecha_caducidad, CURDATE()) <= 7;""")
    caducidades = db.session.execute(query).fetchone()

    query = """ SELECT count(*) as cantidadVentas FROM venta; """
    cantidadVentas = db.session.execute(text(query)).fetchone()

    query = """ SELECT sum(total_ventas) as totalVentas FROM venta; """
    totalVentas = db.session.execute(text(query)).fetchone()

    query = """SELECT ifnull(nombre_paq, nombre_producto) AS productoVendido, COUNT(vi.id_ventaitem) AS cantidad_ventas 
    FROM ventaitem vi 
    LEFT JOIN paquete p on p.id_paquete = vi.paqueteid_itm
    left join producto on id_producto = vi.productoid_itm
    GROUP BY p.nombre_paq
    ORDER BY cantidad_ventas DESC limit 1;"""

    productoVendido = db.session.execute(text(query)).fetchone()

    # Append the results to the data list
    data.append({
        "Caducidades": caducidades.cuenta,
        "cantidadVentas": cantidadVentas.cantidadVentas,
        "totalVentas": totalVentas.totalVentas,
        "productoVendido": productoVendido.productoVendido if productoVendido else "No hay ventas"

    })

    return data

def getProduccion():
    query = """  SELECT prod.nombre_producto as nombre, pi.costo as costo, pi.costo as costo, p.fecha_inicio as fechaInicio,
    CASE 
        WHEN pi.estatus = 0 THEN 'Cancelado'
        ELSE COALESCE(p.fecha_fin, 'En espera')
    END AS fechaFin,  
    CASE 
        WHEN pi.estatus = 0 THEN 2
        WHEN p.fecha_fin IS NULL THEN 0 
        ELSE 1 
    END AS estado_fecha
    FROM produccion p JOIN produccionitem pi ON p.id_produccionitem = pi.id_produccionitem
    join producto prod on prod.id_producto = pi.productoid_itm
    WHERE p.fecha_inicio IS NOT NULL order by  p.fecha_inicio desc limit 6;"""
    # Ejecutar la consulta
    data = db.session.execute(text(query))
    db.session.commit()
    return data
# ''''''''''''''''''''''''CONSULTAS DE BD''''''''''''''''''''''''''''''''

def getProfeCards():
   
    data = []

    query = text(""" select c.id_producto, c.nombre_producto, round((c.costoventa - costoproduccion), 3) utilidad
    from (SELECT id_producto, nombre_producto, alias, dias_caducidadpd, costoproducto costoventa, ROUND(sum((costo_mat * (cantidad + cantidad_merma))), 3) costoproduccion,  CONCAT(ROUND(SUM(cantidad), 2), ' g') peso
    FROM producto p
        inner join recetaitem on productoid_itm = id_producto
        inner join material on materialid_itm = id_material
    WHERE p.estatus = 1 and recetaitem.estatus = 1
    GROUP BY id_producto, nombre_producto, alias, dias_caducidadpd, costoproducto, costoventa) as c ORDER BY utilidad desc limit 1;""")
    utilidadGalleta = db.session.execute(query).fetchone()

    query = """ SELECT p.nombre_paq AS paqueteVendido, COUNT(vi.id_ventaitem) AS cantidad_ventas 
    FROM ventaitem vi 
    JOIN paqueteitem pi ON vi.paqueteid_itm = pi.id_paqueteitem
    join paquete p on p.id_paquete = pi.paqueteid_itm
    GROUP BY p.nombre_paq
    ORDER BY cantidad_ventas DESC limit 1; """
    paqueteVendido = db.session.execute(text(query)).fetchone()

    query = """ select p.nombre_producto as nombre, p.alias, sum(ri.cantidad_merma) as merma
    from producto p 
    join recetaitem ri on p.id_producto = ri.productoid_itm
    group by ri.productoid_itm
    order by merma desc; """
    galletaMerma = db.session.execute(text(query)).fetchone()

    # Append the results to the data list
    data.append({
        "utilidadGalleta": utilidadGalleta.nombre_producto,
        "paqueteVendido": paqueteVendido.paqueteVendido,
        "galletaMerma": galletaMerma.nombre,

    })

    return data


def getProveedoresResponsables():
    query = """  select pi.id_produccionitem as idProduccionItem , min(p.nombre_producto) as productoProducido, min(pi.fecha_registro) as fecha,
        GROUP_CONCAT(DISTINCT m.nombre_mat SEPARATOR ' | ') AS materiales , GROUP_CONCAT(DISTINCT prov.nombre SEPARATOR ' | ') as nombreProveedor,
        u.nombrecompleto as responsable, u.tipousuario as rol
        from produccionitem pi
        join producto p on p.id_producto = pi.productoid_itm
        join recetaitem ri on ri.productoid_itm = p.id_producto
        join material m on m.id_material = ri.materialid_itm
        join compraitem ci on ci.materialid_itm = m.id_material
        join compra c on c.id_compra = ci.compra_itm
        join proveedor prov on prov.id_proveedor = c.proveedorid_comp
        join usuario u on u.id_usuario = pi.usuario_registrado
        group by pi.id_produccionitem
        ORDER BY pi.fecha_registro desc limit 6;  """
    # Ejecutar la consulta
    data = db.session.execute(text(query))
    db.session.commit()
    return data

def getCostoProduccion():
    query = """  SELECT pi.id_produccionitem as idProduccionItem, p.id_producto, p.nombre_producto as nom, ROUND(sum((costo_mat * (ri.cantidad + ri.cantidad_merma))), 3) costoproduccion, max(pi.fecha_registro) as fecha
    FROM producto p
	inner join recetaitem ri on ri.productoid_itm = p.id_producto
	inner join material m on ri.materialid_itm = m.id_material
    left join produccionitem pi on  pi.productoid_itm = p.id_producto
    WHERE p.estatus = 1 and ri.estatus = 1
    GROUP BY pi.id_produccionitem
    order by max(pi.fecha_registro) desc limit 6;"""
    # Ejecutar la consulta
    data = db.session.execute(text(query))
    db.session.commit()
    return data