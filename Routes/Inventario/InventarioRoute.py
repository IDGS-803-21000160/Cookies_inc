
from flask import  render_template, request, redirect, url_for, flash, current_app, Blueprint
from sqlalchemy import text
from flask_login import login_required, current_user
from Entities.InventarioForm import InventarioForm
from Entities.Inventario import Material, Inventario, Movimientos, TipoStock
from Entities.Inventario import Producto

from Entities.InventarioMermaSalida import InventarioMerma, InventarioSalida
from Entities.Inventario import db
from permissions import inventario_required
from datetime  import datetime

modulo_inventario = Blueprint('modulo_inventario', __name__)

@modulo_inventario.route('/inventario',methods=["GET","POST"])
@login_required
@inventario_required
@inventario_required
def inventarios():
    alerta = ''
    success = ''

    if request.args.get('alerta'):
        alerta = request.args.get('alerta')
        success = request.args.get('success')
    #Cambia a stock caducado lo que no esta en merma
    update_query = "UPDATE inventario SET tipostock_inv = 3 WHERE fecha_caducidad <= CAST(NOW() AS DATE) AND tipostock_inv not in (3,4);"
    db.session.execute(text(update_query))
    db.session.commit()
    #Cambia a stock merma y caducado lo que esta en merma
    update_query = "UPDATE inventario SET tipostock_inv = 4 WHERE fecha_caducidad <= CAST(NOW() AS DATE) AND tipostock_inv = 2;"
    db.session.execute(text(update_query))
    db.session.commit()

    consulta = text("""
    SELECT 
    IFNULL(producto_inv, material_inv) id_inv,
    IFNULL(nombre_producto, nombre_mat) nombre, 
    COUNT(DISTINCT id_inventario) lotes,
    nombre_tipoInv tipo_inv,
    ROUND(SUM(IFNULL(costoproducto, costo_mat)), 3) costo,
    ROUND(SUM(cantidad_inv), 2) cantidad_inv,
    tipo_inv id_tipoInv
    FROM inventario
        INNER JOIN tipostock ON id_tipostock = tipostock_inv
        LEFT JOIN producto ON id_producto = producto_inv
        LEFT JOIN material ON id_material = material_inv
        INNER JOIN tipoinventario ON id_tipoInventario = tipo_inv
    WHERE cantidad_inv > 0 and tipostock_inv not in (2, 4, 3)
    GROUP BY id_inv, nombre, tipo_inv, id_tipoInv
    ORDER BY lotes desc;
    """)
    resultados = db.session.execute(consulta)
    return render_template('Inventarios/inventario.html', inventario = resultados, alerta=alerta, success=success)


@modulo_inventario.route('/inventario/lotes',methods=["GET"])
@login_required
@inventario_required
@inventario_required
def lotes():
    id_inv = request.args.get('id_inv')
    id_tipoInv = request.args.get('id_tipoinv')
    print(id_tipoInv)
    consulta = text("""
        SELECT 
        id_inventario,
        tipostock_inv,
        nombre_stock tipo_stock, 
        IFNULL(nombre_producto, nombre_mat) nombre, 
        nombre_tipoInv tipo_inv,
        IFNULL(costoproducto, costo_mat) costo,
        ROUND(cantidad_inv, 2) cantidad_inv,
        fecha_caducidad,
        row_number() over(order by fecha_caducidad desc) as numeroLote
        FROM inventario
            INNER JOIN tipostock ON id_tipostock = tipostock_inv
            LEFT JOIN producto ON id_producto = producto_inv
            LEFT JOIN material ON id_material = material_inv
            INNER JOIN tipoinventario ON id_tipoInventario = tipo_inv
        WHERE (producto_inv = :id_inv or material_inv = :id_inv)  and tipo_inv = :tipo_inv and tipostock_inv in (1,3)
        ORDER BY fecha_caducidad desc;
        """)
    resultados = db.session.execute(consulta, {'id_inv': id_inv, 'tipo_inv': id_tipoInv}).fetchall()
    print(resultados)
    return render_template('Inventarios/inventarioLote.html', inventario = resultados)


@modulo_inventario.route('/inventario/seleccionarTipoEntrada',methods=["GET","POST"])
@login_required
@inventario_required
def tipoEntrada():
    return render_template('Inventarios/seleccionarTipoEntrada.html')


@modulo_inventario.route('/inventario/entradaInventario',methods=["GET","POST"])
@login_required
@inventario_required
def inventariosEntrada():

    alerta = ''
    tipo = ''

    if request.args.get('alerta'):
        alerta = request.args.get('alerta')
        tipo = request.args.get('tipo')
    else:
        tipo = request.form['tipo']
    inventarioForm  = InventarioForm(request.form)

    query =  text("""
    SELECT id_material, nombre_mat,
    CASE WHEN unidad_medida = 'g' THEN 'gramos' WHEN unidad_medida = 'militros' THEN 'Litro' ELSE unidad_medida END unidad_medida
    FROM material
    WHERE estatus = 1;
    """)
    materiales = db.session.execute(query)

    opcionesMateriales = [(material.id_material, '      Ingreso en      '+ material.unidad_medida + '    de   ' + material.nombre_mat) for material in materiales]
    inventarioForm.material.choices = opcionesMateriales

    productos = Producto.query.all() 
    opcionesProducto = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    inventarioForm.producto.choices = opcionesProducto

    return render_template('Inventarios/entradaInventario.html', form = inventarioForm, tipo = tipo, alerta = alerta)


@modulo_inventario.route('/inventario/guardarEntrada', methods=["POST", "GET"])
@login_required
@inventario_required
def inventariosGuardarEntrada():

    entrada = InventarioForm(request.form)
    tipo = request.form['tipo']

    if (entrada.material.data == None and entrada.producto.data == None) or entrada.cantidad.data == None: 
        return redirect(url_for('modulo_inventario.inventariosEntrada', alerta = 'No has ingresado ninguna cantidad', tipo = tipo))

   
    inv = ""
    if tipo == '1':
        materiales = Material.query.all() 
        opcionesMateriales = [(material.id_material, material.nombre_mat) for material in materiales]
        entrada.material.choices = opcionesMateriales
        inv = entrada.material.data
    else:
        productos = Producto.query.all() 
        opcionesProducto = [(producto.id_producto, producto.nombre_producto) for producto in productos]
        entrada.producto.choices = opcionesProducto
        inv = entrada.producto.data

    if request.method == "POST" :
        tipoInv = int(tipo)
        idmateriaproducto = int(inv)
        cantidad = float(entrada.cantidad.data)
        usuariop = current_user.id_usuario
        descripcion = entrada.descripcion.data
        db.session.execute(
                text("CALL entradaInventario(:tipo, :id_materia_producto, :cantidad, :usuariop, :descripcionp)"),
                {"tipo": tipo, "id_materia_producto": idmateriaproducto, "cantidad": cantidad, "usuariop": usuariop, "descripcionp" : descripcion}
            )
        db.session.commit()
    
    return redirect(url_for('modulo_inventario.inventarios', alerta='Entrada de inventario realizada con éxito', success= True))


@modulo_inventario.route('/inventario/confirmarMermas',methods=["GET","POST"])
@login_required
@inventario_required
def confirmarMermas():
    id_inv = int(request.form['id_inv'])
    
    inventarioForm  = InventarioMerma(request.form)
    consulta = text("""
    SELECT 
    id_inventario,
    IFNULL( nombre_producto, nombre_mat ) as nombre, 
    fecha_caducidad,
    cantidad_inv
    FROM inventario
        LEFT JOIN producto on id_producto = producto_inv
        LEFT JOIN material on id_material = material_inv
    WHERE id_inventario = :id_inv;
    """)
    resultados = db.session.execute(consulta.params(id_inv=id_inv)).fetchone()
    print(resultados.nombre)
    return render_template('Inventarios/confirmarMermas.html', form = inventarioForm, resultados = resultados)


@modulo_inventario.route('/inventario/guardarMerma', methods=["POST"])
@login_required
@inventario_required
def inventariosGuardarMerma():
    inventarioF = InventarioMerma(request.form)
    id_inv = request.form['id_inventario']
    usuariop = current_user.id_usuario
    
    if request.method == "POST" and inventarioF.merma.data > 0:

        cantidadInv = Inventario.query.get(id_inv).cantidad_inv

        if inventarioF.merma.data > cantidadInv:
            return redirect(url_for('modulo_inventario.inventarios', alerta='Nmms como vas a quitar mas de lo que tienes papito', success= False))

        db.session.execute(
                text("CALL mermaInventario(:id_inv, :merma, :usuariop)"),
                {"id_inv": id_inv, "merma": inventarioF.merma.data, "usuariop": usuariop}
            )
        db.session.commit()
        return redirect(url_for('modulo_inventario.inventarios', alerta='Se ha añadido merma correctamente!', success= True))
    return redirect(url_for('modulo_inventario.inventarios', alerta='Error al añadir merma!', success= False))


@modulo_inventario.route('/inventario/salidaInventario', methods=["POST"])
@login_required
@inventario_required
def inventariosSalida():
    id_inv = int(request.form['id_inv'])
    
    inventarioForm  = InventarioSalida(request.form)
    consulta = text("""
    SELECT 
    id_inventario,
    tipostock_inv,
    IFNULL( nombre_producto, nombre_mat ) as nombre, 
    fecha_caducidad,
    cantidad_inv
    FROM inventario
        LEFT JOIN producto on id_producto = producto_inv
        LEFT JOIN material on id_material = material_inv
    WHERE id_inventario = :id_inv;
    """)
    resultados = db.session.execute(consulta.params(id_inv=id_inv)).fetchone()
    return render_template('Inventarios/confirmarSalida.html', form = inventarioForm, resultados = resultados)


@modulo_inventario.route('/inventario/guardarSalida', methods=["POST"])
@login_required
@inventario_required
def inventariosGuardarSalida():
    inventarioF = InventarioSalida(request.form)
    id_inv = request.form['id_inventario']
    inventario = Inventario.query.get(id_inv)

    if request.method == "POST" and inventarioF.validate():
        if inventarioF.cantidad.data > inventario.cantidad_inv:
            return redirect(url_for('modulo_inventario.inventarios', alerta='No hay suficiente existencia en inventario!', success= False)) 
        
        inventario.cantidad_inv = inventario.cantidad_inv - inventarioF.cantidad.data
        tipomov = 'SALIDA DE MATERIAL EN STOCK' if inventario.tipo_inv == 1 else 'SALIDA DE PRODUCTO TERMINADO EN STOCK'
        resultado = db.session.query(Inventario, TipoStock)\
                      .filter(Inventario.id_inventario == id_inv)\
                      .join(TipoStock, Inventario.tipostock_inv == TipoStock.id_tipostock)\
                      .first()
        movimiento = Movimientos(
            usuarioid_movinv = current_user.id_usuario,
            fecha_movimiento = datetime.now(),
            inventarioid_movinv = int(id_inv),
            cantidad_movinv = int (inventarioF.cantidad.data),
            descripcion_movinv = inventarioF.descripcion.data,
            tipomovimiento_movinv = tipomov + '  ' + str(resultado.TipoStock.nombre_stock)
        )
        db.session.add(movimiento)
        db.session.commit()
        
        if inventario.tipostock_inv == 2 or inventario.tipostock_inv == 4:
            return redirect(url_for('modulo_inventario.mermas'))
        else:
            return redirect(url_for('modulo_inventario.inventarios', alerta='Salida de inventario realizada con éxito', success= True))
    
    return render_template('Inventarios/confirmarSalida.html', form=inventarioF, resultados=inventario, alerta='Error al realizar la salida', success= False)


@modulo_inventario.route('/inventario/mermas',methods=["GET","POST"])
@login_required
@inventario_required
def mermas():
    
    consulta = text("""
    SELECT 
    id_inventario,
    tipostock_inv,
    cast(inventario.fecha_registro as date) fecha_merma,
    IFNULL( nombre_producto, nombre_mat ) nombre, 
    nombre_tipoInv tipo_inv,
    IFNULL ( costoproducto, costo_mat ) costo,
    fecha_caducidad,
    cantidad_inv
    FROM inventario
        INNER JOIN tipostock on id_tipostock = tipostock_inv
        LEFT JOIN producto on id_producto = producto_inv
        LEFT JOIN material on id_material = material_inv
        INNER JOIN tipoinventario on id_tipoInventario = tipo_inv
    WHERE tipostock_inv in (2, 4) and cantidad_inv > 0
    ORDER BY 6, 3;
    """)
    resultados = db.session.execute(consulta)

    return render_template('Inventarios/Mermas/mermas.html', inventario = resultados)

@modulo_inventario.route('/inventario/movimientos', methods=['GET', 'POST'])
@login_required
@inventario_required
@inventario_required
def movimientos():
    consulta = text("""
    SELECT 
        nombrecompleto responsable
        , fecha_movimiento fecha
        , productomaterial
        , fecha_caducidad caducaLote
        , cantidad_movinv cantidad
        , id_inventario lote
        , descripcion_movinv
        , tipomovimiento_movinv
    FROM movimientos_inventario
        INNER JOIN usuario on id_usuario = usuarioid_movinv
        INNER JOIN (
            select id_inventario, ifnull(nombre_mat, nombre_producto) productomaterial, fecha_caducidad 
            from inventario
                left join material on material_inv = id_material
                left join producto on producto_inv = id_producto
        ) inv on inv.id_inventario = inventarioid_movinv
    """)
    movimientos = db.session.execute(consulta)
    return render_template('Inventarios/Movimientos/movimientos.html', movimientos=movimientos)

@modulo_inventario.route('/inventario/devolverMerma', methods=['POST'])
@login_required
@inventario_required
@inventario_required
def devolverMerma():
    id_inv = request.form['id_inv']
    form = InventarioSalida(request.form)

    consulta = text("""
    SELECT
    id_inventario,
    IFNULL( nombre_producto, nombre_mat ) nombre,
    fecha_caducidad,
    cantidad_inv
    FROM inventario
        INNER JOIN tipostock on id_tipostock = tipostock_inv
        LEFT JOIN producto on id_producto = producto_inv
        LEFT JOIN material on id_material = material_inv
        INNER JOIN tipoinventario on id_tipoInventario = tipo_inv
    WHERE id_inventario = :id_inv;
    """)
    resultados = db.session.execute(consulta.params(id_inv=id_inv)).fetchone()
    return render_template('Inventarios/Mermas/confirmarDevolucionMerma.html', resultados=resultados, form = form)

@modulo_inventario.route('/inventario/guardarDevolucionMerma', methods=['POST'])
@login_required
@inventario_required
@inventario_required
def guardarDevolucionMerma():
    id_inv = request.form['id_inventario']
    form = InventarioSalida(request.form)

    if request.method == "POST" and form.validate():
        cantidad = form.cantidad.data
        descripcion = form.descripcion.data
        usuariop = current_user.id_usuario

        db.session.execute(
            text("CALL devolucionMerma(:idinv, :cantidadp, :usuariop, :descripcionp)"),
            {"idinv": id_inv, "cantidadp": cantidad, "usuariop": usuariop, "descripcionp": descripcion}
        )
        db.session.commit()
        return redirect(url_for('modulo_inventario.mermas', alerta='Devolución de merma realizada con éxito', success= 'True'))
    return redirect(url_for('modulo_inventario.mermas', alerta='Error al realizar la devolución', success= 'False'))