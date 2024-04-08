
from flask import  render_template, request, redirect, url_for, flash, current_app, Blueprint
from sqlalchemy import text
from flask_login import login_required

# from Entities.InventarioForm import InventarioForm
from Entities.InventarioForm import InventarioForm
from Entities.InventarioMaterialForm import InventarioMaterialForm
from Entities.InventarioProductoForm import InventarioProductoForm
from Entities.Inventario import Material, TipoStock, Inventario, TipoInventario, RecetaItem, Paquete, PaqueteItem
from Entities.Inventario import Producto
from Entities.PaqueteForm import PaqueteForm
from datetime import datetime




from Entities.InventarioMermaSalida import InventarioMerma, InventarioSalida
from Entities.Inventario import db

modulo_inventario = Blueprint('modulo_inventario', __name__)

# csrf=CSRFProtect()

@modulo_inventario.route('/inventario',methods=["GET","POST"])
@login_required
def inventarios():
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
    SUM(IFNULL(costoproducto, costo_mat)) costo,
    ROUND(SUM(cantidad_inv), 2) cantidad_inv,
    tipo_inv id_tipoInv
    FROM inventario
        INNER JOIN tipostock ON id_tipostock = tipostock_inv
        LEFT JOIN producto ON id_producto = producto_inv
        LEFT JOIN material ON id_material = material_inv
        INNER JOIN tipoinventario ON id_tipoInventario = tipo_inv
    WHERE cantidad_inv > 0 and tipostock_inv not in (2, 4)
    GROUP BY id_inv, nombre, tipo_inv, id_tipoInv
    ORDER BY lotes desc;
    """)
    resultados = db.session.execute(consulta)
    return render_template('Inventarios/inventario.html', inventario = resultados)

@modulo_inventario.route('/inventario/lotes',methods=["GET"])
@login_required
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
def tipoEntrada():
    return render_template('Inventarios/seleccionarTipoEntrada.html')

@modulo_inventario.route('/inventario/entradaInventario',methods=["GET","POST"])
@login_required
def inventariosEntrada():
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

    return render_template('Inventarios/entradaInventario.html', form = inventarioForm, tipo = tipo)


@modulo_inventario.route('/inventario/guardarEntrada', methods=["POST"])
@login_required
def inventariosGuardarEntrada():

    tipo = request.form['tipo']
    entrada = InventarioForm(request.form)
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
        usuariop = 2
        db.session.execute(
                text("CALL entradaInventario(:tipo, :id_materia_producto, :cantidad, :usuariop)"),
                {"tipo": tipo, "id_materia_producto": idmateriaproducto, "cantidad": cantidad, "usuariop": usuariop}
            )
        db.session.commit()
    
    flash('Entrada de inventario guardada correctamente', 'success')
    return redirect(url_for('modulo_inventario.inventarios'))


@modulo_inventario.route('/inventario/confirmarMermas',methods=["GET","POST"])
@login_required
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
def inventariosGuardarMerma():
    inventarioF = InventarioMerma(request.form)
    id_inv = request.form['id_inventario']
    usuariop = 2
    
    if request.method == "POST" and inventarioF.validate():

        db.session.execute(
                text("CALL mermaInventario(:id_inv, :merma, :usuariop)"),
                {"id_inv": id_inv, "merma": inventarioF.merma.data, "usuariop": usuariop}
            )
        db.session.commit()
        flash('Merma guardada correctamente', 'success')
        return redirect(url_for('modulo_inventario.inventarios'))

@modulo_inventario.route('/inventario/salidaInventario', methods=["POST"])
@login_required
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
def inventariosGuardarSalida():
    inventarioF = InventarioSalida(request.form)
    id_inv = request.form['id_inventario']
    inventario = Inventario.query.get(id_inv)

    if request.method == "POST" and inventarioF.validate():
        inventario.cantidad_inv = inventario.cantidad_inv - inventarioF.cantidad.data
        db.session.commit()
        if inventario.tipostock_inv == 2 or inventario.tipostock_inv == 4:
            return redirect(url_for('mermas'))
        else:
            return redirect(url_for('modulo_inventario.inventarios'))
    
    return render_template('Inventarios/confirmarSalida.html', form=inventarioF, resultados=inventario)


@modulo_inventario.route('/inventario/mermas',methods=["GET","POST"])
@login_required
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

# .......................................................

@modulo_inventario.route('/inventario/materiales',methods=["GET","POST"])
@login_required
def materiales():
    query =  text("""
    SELECT id_material, nombre_mat, dias_caducidad,
    CASE WHEN unidad_medida = 'g' THEN 'Kg' WHEN unidad_medida = 'ml' THEN 'Litro' ELSE unidad_medida END unidad_medida, 
    IF(unidad_medida in ('g', 'ml'), ROUND(costo_mat * 1000, 2), costo_mat) costo_mat, fecha_registro
    FROM material
    WHERE estatus = 1;
    """)
    materiales = db.session.execute(query)
    return render_template('Inventarios/Materiales/materiales.html', materiales=materiales)

@modulo_inventario.route('/inventario/agregarMaterial',methods=["GET","POST"])
@login_required
def inventariosAddMaterial():
    materialForm  = InventarioMaterialForm(request.form)
    return render_template('Inventarios/Materiales/agregarMaterial.html', form = materialForm)

@modulo_inventario.route('/inventario/editarMaterial', methods=["GET", "POST"])
@login_required
def editarMaterial():
    id_material = request.form['material_id']
    material = Material.query.get(id_material)
    materialForm = InventarioMaterialForm(request.form, obj=material)
    materialForm.unidadMedidaAgregar.data = material.unidad_medida
    if materialForm.unidadMedidaAgregar.data == 'g' or materialForm.unidadMedidaAgregar.data == 'ml':
        materialForm.costoMaterial.data = material.costo_mat * 1000
        material.costo_mat = material.costo_mat * 1000 
        if materialForm.unidadMedidaAgregar.data == 'g':
            materialForm.unidadMedidaAgregar.data = 'Kg'
        else :
            materialForm.unidadMedidaAgregar.data = 'Litro'
    return render_template('Inventarios/Materiales/modificarMaterial.html', form=materialForm, material=material)

@modulo_inventario.route('/inventario/guardarMaterial', methods=["POST"])
@login_required
def inventariosGuardarMaterial():   
    materialF = InventarioMaterialForm(request.form)

    if request.method == "POST" and materialF.validate():

        costomaterial = float(materialF.costoMaterial.data)
        unidad = materialF.unidadMedidaAgregar.data

        if materialF.unidadMedidaAgregar.data == 'Kg' or materialF.unidadMedidaAgregar.data == 'Litro':
            costomaterial = costomaterial / 1000
            if materialF.unidadMedidaAgregar.data == 'Kg':
                unidad = 'g'
            else:
                unidad = 'ml'

        nuevo_material = Material(
        nombre_mat=materialF.nombreMaterial.data,
        dias_caducidad=int(materialF.diasCaducidad.data),
        unidad_medida=unidad,
        costo_mat=costomaterial,
        estatus=1,  # Puedes establecer el valor de estatus aquí si es necesario
        usuario_registro=1,  # Puedes establecer el usuario de registro aquí si es necesario
        fecha_registro=datetime.now()  # Puedes establecer la fecha de registro aquí si es necesario
        )
        db.session.add(nuevo_material)
        db.session.commit()
        flash('Material guardado correctamente', 'success')
        return redirect(url_for('materiales'))  # Redirige a donde quieras después de guardar el material
    
    return render_template('Inventarios/Materiales/agregarMaterial.html', form=materialF)

@modulo_inventario.route('/inventario/eliminarMaterial', methods=["POST"])
@login_required
def eliminarMaterial():
    id_material = request.form['material_id']
    material = Material.query.get(id_material)
    material.estatus = 0
    db.session.commit()
    flash('Material eliminado correctamente', 'success')
    return redirect(url_for('materiales'))

@modulo_inventario.route('/inventario/actualizarMaterial', methods=["POST"])
@login_required
def actualizarMaterial():
    id_material = request.form['material_id']
    material = Material.query.get(id_material)
    materialForm = InventarioMaterialForm(request.form)
    if request.method == "POST" and materialForm.validate():

        costomaterial = float(materialForm.costoMaterial.data)
        unidad = materialForm.unidadMedidaAgregar.data

        if materialForm.unidadMedidaAgregar.data == 'Kg' or materialForm.unidadMedidaAgregar.data == 'Litro':
            costomaterial = costomaterial / 1000
            if materialForm.unidadMedidaAgregar.data == 'Kg':
                unidad = 'g'
            else:
                unidad = 'ml'
        
        material.nombre_mat = materialForm.nombreMaterial.data
        material.dias_caducidad = materialForm.diasCaducidad.data
        material.unidad_medida = unidad
        material.costo_mat = costomaterial
        db.session.commit()
        flash('Material actualizado correctamente', 'success')
        return redirect(url_for('materiales'))
    return render_template('Inventarios/Materiales/modificarMaterial.html', form=materialForm, material=material)

# .....................................................

tabladatos = []

@modulo_inventario.route('/inventario/agregarProducto',methods=["GET","POST"])
@login_required
def inventariosAddProducto():
    tabladatos.clear()
    productoForm  = InventarioProductoForm(request.form)
    ingredientes = Material.query.all()
    opciones = [
    (
        receta.id_material,
        receta.nombre_mat + ' en ' +
        ('gramos' if receta.unidad_medida == 'g' else 'mililitros' if receta.unidad_medida == 'ml' else receta.unidad_medida)
    ) 
    for receta in ingredientes
    ]
    productoForm.materiales.choices = opciones
    return render_template('Inventarios/Producto/agregarProducto.html', form = productoForm, tabladatos = tabladatos, costoProduccion = 0)


@modulo_inventario.route('/inventario/guardarProducto', methods=["POST"])
@login_required
def inventariosGuardarProducto():
    productoF = InventarioProductoForm(request.form)
    # Indica que no ha sido asignado aún.
        
    costoProduccion = 0
    ingredientes = Material.query.all()
    opciones = [
    (
        receta.id_material,
        receta.nombre_mat + ' en ' +
        ('gramos' if receta.unidad_medida == 'g' else 'mililitros' if receta.unidad_medida == 'ml' else receta.unidad_medida)
    ) 
    for receta in ingredientes
    ]
    productoF.materiales.choices = opciones

    # Verifica qué botón se presionó
    if request.form['action'] == 'agregar_item':
        # Lógica para agregar ingredientes a la lista
        cantidad = request.form.get("cantidad", type=float)
        merma = request.form.get("merma", type=float)
        id_material = productoF.materiales.data
        nombre_material = next((nombre_mat for id_mat, nombre_mat in opciones if id_mat == id_material), None)
        
        if nombre_material and nombre_material not in [item['nombre_material'] for item in tabladatos]:
            costo = Material.query.get(id_material)
            tabladatos.append({"id_material": id_material, "nombre_material": nombre_material, "cantidad": cantidad, "merma" : merma, "costo": costo.costo_mat})

            costoProduccion = round(sum([float(item['costo']) * ((float(item['cantidad']) + float(item['merma'])) / 50)  for item in tabladatos]), 2)
            
        return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos, costoProduccion = costoProduccion)  # Mantén al usuario en la misma página

    elif request.form['action'] == 'guardar_producto':
        # Lógica para guardar el producto completo
        if tabladatos == []:
            flash('No se han agregado ingredientes al producto', 'danger')
            return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos, costoProduccion = 0)
        else: 
            nuevo_producto = Producto(
                nombre_producto=productoF.nombreProducto.data,
                alias=productoF.alias.data,
                estatus=1,
                usuario_registro=1,
                fecha_registro=datetime.now(),
                costoproducto=productoF.costoProducto.data,
                dias_caducidadpd=productoF.diasCaducidad.data,
            )
            db.session.add(nuevo_producto)
            db.session.commit()
            id_producto = nuevo_producto.id_producto
            print(id_producto)

            for item in tabladatos:
                addItem = RecetaItem(
                    productoid_itm=id_producto,
                    materialid_itm=item['id_material'],
                    cantidad= float(item['cantidad']) / 50,
                    estatus=1,
                    usuario_registro=1,
                    fecha_registro=datetime.now(),
                    cantidad_merma = float(item['merma']) / 50
                )
                db.session.add(addItem)
                db.session.commit()
            tabladatos.clear()

            return redirect(url_for('modulo_inventario.productos'))  # Redirige después de guardar
    elif request.form['action'] == 'quitar':
        # Lógica para quitar ingredientes de la lista
        id_material = request.form['id_material']
        tabladatos[:] = [item for item in tabladatos if item['id_material'] != int(id_material)]
        costoProduccion = round(sum([float(item['costo']) * (float(item['cantidad']) + float(item['merma'])) for item in tabladatos]), 2)
        return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos, costoProduccion = costoProduccion)

    return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos, costoProduccion = costoProduccion)

@modulo_inventario.route('/inventario/productos',methods=["GET","POST"])
@login_required
def productos():
    # productos = Producto.query.join(RecetaItem, Producto.id_producto == RecetaItem.productoid_itm).filter(Producto.estatus == 1 and RecetaItem.estatus == 1).all()
    consulta = text("""
    SELECT id_producto, nombre_producto, alias, dias_caducidadpd, costoproducto costoventa, ROUND(sum((costo_mat * (cantidad + cantidad_merma))), 3) costoproduccion,  CONCAT(ROUND(SUM(cantidad), 2), ' g') peso
    FROM producto p
        inner join recetaitem on productoid_itm = id_producto
        inner join material on materialid_itm = id_material
    WHERE p.estatus = 1 and recetaitem.estatus = 1
    GROUP BY id_producto, nombre_producto, alias, dias_caducidadpd, costoproducto, costoventa;
    """)
    productos = db.session.execute(consulta)
    return render_template('Inventarios/Producto/productos.html', productos=productos)

@modulo_inventario.route('/inventario/detalle', methods=["GET", "POST"])
@login_required
def verReceta():
    tabladatos.clear()
    id_producto = request.form['id_producto']
    consulta = text("""
    SELECT nombre_producto, nombre_mat, cantidad
    FROM recetaitem
    inner join material on id_material = materialid_itm
    inner join producto on id_producto = productoid_itm
    WHERE productoid_itm = :id_producto;
    """)
    resultados = db.session.execute(consulta.params(id_producto=id_producto))
    producto = Producto.query.get(id_producto)
    return render_template('Inventarios/Producto/detalleProducto.html', materiales=resultados, producto = producto)

@modulo_inventario.route('/inventario/eliminarProducto', methods=["POST"])
@login_required
def eliminarProducto():
    id_producto = request.form['id_producto']
    producto = Producto.query.get(id_producto)
    producto.estatus = 0
    db.session.commit()
    receta = RecetaItem.query.filter_by(productoid_itm=id_producto).all()
    for item in receta:
        item.estatus = 0
        db.session.commit()
    flash('Producto eliminado correctamente', 'success')
    return redirect(url_for('productos'))

@modulo_inventario.route('/inventario/editarProducto', methods=["GET", "POST"])
@login_required
def editarProducto():
    tabladatos.clear()
    id_producto = request.form['id_producto']
    producto = Producto.query.get(id_producto)
    productoForm = InventarioProductoForm(request.form)
    ingredientes = Material.query.all()
    opciones = [(receta.id_material, receta.nombre_mat) for receta in ingredientes]
    productoForm.materiales.choices = opciones

    consulta = text("""
    SELECT nombre_producto, nombre_mat, cantidad, materialid_itm
    FROM recetaitem
    inner join material on id_material = materialid_itm
    inner join producto on id_producto = productoid_itm
    WHERE productoid_itm = :id_producto;
    """)
    ingredientes = db.session.execute(consulta.params(id_producto=id_producto))
    
    for item in ingredientes:
        tabladatos.append({"id_material": item.materialid_itm, "nombre_material": item.nombre_mat, "cantidad" : item.cantidad})
    print(tabladatos)
    return render_template('Inventarios/Producto/modificarProducto.html', form=productoForm, producto=producto, tabladatos=tabladatos)

@modulo_inventario.route('/inventario/actualizarProducto', methods=["POST"])
@login_required
def actualizarProducto():
    productoF = InventarioProductoForm(request.form)
    ingredientes = Material.query.all()
    opciones = [(receta.id_material, receta.nombre_mat) for receta in ingredientes]
    productoF.materiales.choices = opciones
    id_producto = request.form['id_producto']
    producto = Producto.query.get(id_producto)
    
    # Verifica qué botón se presionó
    if request.form['action'] == 'agregar_item':
        # Lógica para agregar ingredientes a la lista
        cantidad = request.form.get("cantidad", type=int)
        id_material = productoF.materiales.data
        nombre_material = next((nombre_mat for id_mat, nombre_mat in opciones if id_mat == id_material), None)
        if nombre_material and nombre_material not in [item['nombre_material'] for item in tabladatos]:
            tabladatos.append({"id_material": id_material, "nombre_material": nombre_material, "cantidad": cantidad})
        redirect(url_for('modulo_inventario.editarProducto', id_producto=id_producto))  # Mantén al usuario en la misma página
        # return render_template('Inventarios/Producto/modificarProducto.html', form=productoF, tabladatos=tabladatos, producto=producto)
    # elif request.form['action'] == 'quitar':
    #     # Lógica para quitar ingredientes de la lista
    #     id_material = request.form['id_material']
    #     print(id_material)
    #     tabladatos[:] = [item for item in tabladatos if item['id_material'] != int(id_material)]
        
        return render_template('Inventarios/Producto/modificarProducto.html', form=productoF, tabladatos=tabladatos, producto=producto)
    elif request.form['action'] == 'guardar_producto':
        # Lógica para guardar el producto completo
        producto = Producto.query.get(id_producto)
        producto.nombre_producto = productoF.nombreProducto.data
        producto.alias = productoF.alias.data
        producto.costoproducto = productoF.costoProducto.data
        producto.dias_caducidadpd = productoF.diasCaducidad.data
        db.session.commit()

        receta = RecetaItem.query.filter_by(productoid_itm=id_producto).all()
        for item in receta:
            db.session.delete(item)
            db.session.commit()

        for item in tabladatos:
            addItem = RecetaItem(
                productoid_itm=id_producto,
                materialid_itm=item['id_material'],
                cantidad=item['cantidad'],
                estatus=1,
                usuario_registro=1,
                fecha_registro=datetime.now()
            )
            db.session.add(addItem)
            db.session.commit()
        tabladatos.clear()

        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('modulo_inventario.productos'))
    return render_template('Inventarios/Producto/modificarProducto.html', form=productoF, tabladatos=tabladatos, producto=producto)

@modulo_inventario.route('/inventario/eliminarIngrediente', methods=["POST"])
@login_required
def eliminarIngrediente():
    id_material = request.form['id_material']
    id_producto = request.form['id_producto']
    producto = Producto.query.get(id_producto)
    productoForm = InventarioProductoForm(request.form)
    ingredientes = Material.query.all()
    opciones = [(receta.id_material, receta.nombre_mat) for receta in ingredientes]
    productoForm.materiales.choices = opciones
    tabladatos[:] = [item for item in tabladatos if item['id_material'] != int(id_material)]
    return render_template('Inventarios/Producto/modificarProducto.html', form=productoForm, tabladatos=tabladatos, producto=producto)

#.....................................................

@modulo_inventario.route('/paquetes')
@login_required
def paquetes():
    query =  text("""
    SELECT id_paquete, nombre_paq, costopaquete_paq, cantidadproductos_paq
    FROM paquete
    WHERE estatus = 1;
    """)
    paquete = db.session.execute(query)
    return render_template('Paquetes/paquetes.html', paquetes = paquete)

@modulo_inventario.route('/paquetes/detalle', methods=["GET", "POST"])
@login_required
def verDetalle():
    id_paquete = request.form['id_paquete']
    consulta = text("""
    SELECT nombre_producto nombreproducto, alias, costoproducto costoventa, CONCAT(ROUND(SUM(cantidad), 2), ' g') peso, cantidadproducto_itm cantidad
    FROM paqueteitem
        INNER JOIN producto on id_producto = productoid_itm
        INNER JOIN recetaitem on id_producto = recetaitem.productoid_itm
        INNER JOIN material on id_material = materialid_itm
    WHERE paqueteid_itm = :id_paquete
    GROUP BY 1,2,3;
    """)
    resultados = db.session.execute(consulta.params(id_paquete=id_paquete))
    paquete = Paquete.query.get(id_paquete)
    return render_template('Paquetes/paquetesDetalle.html', productos=resultados, paquete = paquete)

productosPaquete = []

@modulo_inventario.route('/paquetes/agregarPaquete',methods=["GET","POST"])
@login_required
def inventariosAddPaquete():
    productosPaquete.clear()
    paqueteForm  = PaqueteForm(request.form)
    consulta = text("""
    SELECT id_producto, CONCAT( nombre_producto, '  |     peso de    ',  ROUND(SUM(cantidad), 3), '  g', '     | costo de    $', costoproducto ) nombre_producto
    FROM producto
        inner join recetaitem on id_producto = productoid_itm
        inner join material on id_material = materialid_itm
    where producto.estatus = 1
    group by id_producto, nombre_producto;
    """)
    productos = db.session.execute(consulta)
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteForm.productos.choices = opciones
    return render_template('Paquetes/agregarPaquete.html', form = paqueteForm, productosPaquete = productosPaquete)

@modulo_inventario.route('/paquetes/guardarPaquete', methods=["POST"])
@login_required
def inventariosGuardarPaquete():
    paqueteF = PaqueteForm(request.form)
    productos = Producto.query.all()
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteF.productos.choices = opciones

    # Verifica qué botón se presionó
    if request.form['action'] == 'agregar_item':
        # Lógica para agregar ingredientes a la lista
        cantidad = request.form.get("cantidad", type=int)
        id_producto = paqueteF.productos.data
        nombre_producto = next((nombre_pd for id_pd, nombre_pd in opciones if id_pd == id_producto), None)
        if nombre_producto and nombre_producto not in [item['nombre_producto'] for item in productosPaquete]:
            productosPaquete.append({"id_producto": id_producto, "nombre_producto": nombre_producto, "cantidad": cantidad})
        return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete)
    
    elif request.form['action'] == 'guardar_paquete':

        if productosPaquete == []:
            flash('No se han agregado productos al paquete', 'danger')
            return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete)
        else: 
            nuevo_paquete = Paquete(
                nombre_paq=paqueteF.nombrePaquete.data,
                costopaquete_paq=paqueteF.costoPaquete.data,
                cantidadproductos_paq=len(productosPaquete),
                estatus=1,
                usuarioregistro=1,
                fecha_registro=datetime.now()
            )
            db.session.add(nuevo_paquete)
            db.session.commit()
            id_paquete = nuevo_paquete.id_paquete

            for item in productosPaquete:
                addItem = PaqueteItem(
                    paqueteid_itm=id_paquete,
                    productoid_itm=item['id_producto'],
                    cantidadproducto_itm=item['cantidad'],
                    estatus=1,
                    usuarioregistro=1,
                    fecha_registro=datetime.now()
                )
                db.session.add(addItem)
                db.session.commit()
            productosPaquete.clear()

            return redirect(url_for('modulo_inventario.paquetes'))
    else:
        return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete)

@modulo_inventario.route('/paquetes/editarPaquete', methods=["GET", "POST"])
@login_required
def editarPaquete():
    productosPaquete.clear()
    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)
    paqueteForm = PaqueteForm(request.form)
    productos = Producto.query.all()
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteForm.productos.choices = opciones

    consulta = text("""
    SELECT productoid_itm, nombre_producto, cantidadproducto_itm cantidad
    FROM paqueteitem
        INNER JOIN producto on id_producto = productoid_itm
    WHERE paqueteid_itm = :id_paquete;
    """)
    ingredientes = db.session.execute(consulta.params(id_paquete=id_paquete))
    
    for item in ingredientes:
        productosPaquete.append({"id_producto": item.productoid_itm, "nombre_producto": item.nombre_producto, "cantidad" : item.cantidad})
    return render_template('Paquetes/modificarPaquete.html', form=paqueteForm, paquete=paquete, productosPaquete=productosPaquete)

@modulo_inventario.route('/paquetes/actualizarPaquete', methods=["POST"])
@login_required
def actualizarPaquete():
    paqueteF = PaqueteForm(request.form)
    productos = Producto.query.all()
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteF.productos.choices = opciones
    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)

    # Verifica qué botón se presionó
    
    if request.form['action'] == 'agregar_item':
        # Lógica para agregar ingredientes a la lista
        cantidad = request.form.get("cantidad", type=int)
        id_producto = paqueteF.productos.data
        nombre_producto = next((nombre_pd for id_pd, nombre_pd in opciones if id_pd == id_producto), None)
        if nombre_producto and nombre_producto not in [item['nombre_producto'] for item in productosPaquete]:
            productosPaquete.append({"id_producto": id_producto, "nombre_producto": nombre_producto, "cantidad": cantidad})
        return render_template('Paquetes/modificarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, paquete=paquete)
    
    elif request.form['action'] == 'guardar_paquete':
        # Lógica para guardar el producto completo
        if productosPaquete == []:
            flash('No se han agregado productos al paquete', 'danger')
            return render_template('Paquetes/modificarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, paquete=paquete)
        else: 
            paquete.nombre_paq = paqueteF.nombrePaquete.data
            paquete.costopaquete_paq = paqueteF.costoPaquete.data
            paquete.cantidadproductos_paq = len(productosPaquete)
            db.session.commit()

            paqueteitems = PaqueteItem.query.filter_by(paqueteid_itm=id_paquete).all()
            for item in paqueteitems:
                db.session.delete(item)
                db.session.commit()

            for item in productosPaquete:
                addItem = PaqueteItem(
                    paqueteid_itm=id_paquete,
                    productoid_itm=item['id_producto'],
                    cantidadproducto_itm=item['cantidad'],
                    estatus=1,
                    usuarioregistro=1,
                    fecha_registro=datetime.now()
                )
                db.session.add(addItem)
                db.session.commit()
            productosPaquete.clear()

            flash('Paquete actualizado correctamente', 'success')
            return redirect(url_for('modulo_inventario.paquetes'))

@modulo_inventario.route('/paquetes/eliminarProducto', methods=["POST"])
@login_required
def eliminarProductoPaquete():
    id_producto = request.form['id_producto']
    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)
    paqueteForm  = PaqueteForm(request.form)
    productos = Producto.query.all()
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteForm.productos.choices = opciones
    productosPaquete[:] = [item for item in productosPaquete if item['id_producto'] != int(id_producto)]
    return render_template('Paquetes/modificarPaquete.html', form=paqueteForm, productosPaquete=productosPaquete, paquete=paquete)

@modulo_inventario.route('/paquetes/eliminarPaquete', methods=["POST"])
@login_required
def eliminarPaquete():
    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)
    paquete.estatus = 0
    db.session.commit()
    paqueteitems = PaqueteItem.query.filter_by(paqueteid_itm=id_paquete).all()
    for item in paqueteitems:
        item.estatus = 0
        db.session.commit()
    

    return redirect(url_for('modulo_inventario.paquetes'))