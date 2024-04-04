
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
import datetime

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
        id_inventario,
        tipostock_inv,
        nombre_stock tipo_stock, 
        IFNULL(nombre_producto, nombre_mat) nombre, 
        nombre_tipoInv tipo_inv,
        IFNULL(costoproducto, costo_mat) costo,
        fecha_caducidad,
        ROUND(cantidad_inv, 2) cantidad_inv
    FROM inventario
        INNER JOIN tipostock ON id_tipostock = tipostock_inv
        LEFT JOIN producto ON id_producto = producto_inv
        LEFT JOIN material ON id_material = material_inv
        INNER JOIN tipoinventario ON id_tipoInventario = tipo_inv
    WHERE cantidad_inv > 0 and tipostock_inv not in (2, 4)
    ORDER BY 6, 3;
    """)
    resultados = db.session.execute(consulta)

    return render_template('Inventarios/inventario.html', inventario = resultados)


@modulo_inventario.route('/inventario/seleccionarTipoEntrada',methods=["GET","POST"])
def tipoEntrada():
    return render_template('Inventarios/seleccionarTipoEntrada.html')

@modulo_inventario.route('/inventario/entradaInventario',methods=["GET","POST"])
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
            return redirect(url_for('inventarios'))
    
    return render_template('Inventarios/confirmarSalida.html', form=inventarioF, resultados=inventario)

@modulo_inventario.route('/inventario/mermas',methods=["GET","POST"])
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
def inventariosAddMaterial():
    materialForm  = InventarioMaterialForm(request.form)
    return render_template('Inventarios/Materiales/agregarMaterial.html', form = materialForm)

@modulo_inventario.route('/inventario/editarMaterial', methods=["GET", "POST"])
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
def eliminarMaterial():
    id_material = request.form['material_id']
    material = Material.query.get(id_material)
    material.estatus = 0
    db.session.commit()
    flash('Material eliminado correctamente', 'success')
    return redirect(url_for('materiales'))

@modulo_inventario.route('/inventario/actualizarMaterial', methods=["POST"])
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
def inventariosAddProducto():
    tabladatos.clear()
    productoForm  = InventarioProductoForm(request.form)
    ingredientes = Material.query.all()
    opciones = [(receta.id_material, receta.nombre_mat) for receta in ingredientes]
    productoForm.materiales.choices = opciones
    return render_template('Inventarios/Producto/agregarProducto.html', form = productoForm, tabladatos = tabladatos)

@modulo_inventario.route('/inventario/guardarProducto', methods=["POST"])
def inventariosGuardarProducto():
    productoF = InventarioProductoForm(request.form)
    ingredientes = Material.query.all()
    opciones = [(receta.id_material, receta.nombre_mat) for receta in ingredientes]
    productoF.materiales.choices = opciones

    # Verifica qué botón se presionó
    if request.form['action'] == 'agregar_item':
        # Lógica para agregar ingredientes a la lista
        cantidad = request.form.get("cantidad", type=int)
        id_material = productoF.materiales.data
        nombre_material = next((nombre_mat for id_mat, nombre_mat in opciones if id_mat == id_material), None)
        if nombre_material and nombre_material not in [item['nombre_material'] for item in tabladatos]:
            tabladatos.append({"id_material": id_material, "nombre_material": nombre_material, "cantidad": cantidad})
        return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos)  # Mantén al usuario en la misma página

    elif request.form['action'] == 'guardar_producto':
        # Lógica para guardar el producto completo
        if tabladatos == []:
            flash('No se han agregado ingredientes al producto', 'danger')
            return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos)
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
                    cantidad=item['cantidad'],
                    estatus=1,
                    usuario_registro=1,
                    fecha_registro=datetime.now()
                )
                db.session.add(addItem)
                db.session.commit()
            tabladatos.clear()

            return redirect(url_for('productos'))  # Redirige después de guardar
    elif request.form['action'] == 'quitar':
        # Lógica para quitar ingredientes de la lista
        id_material = request.form['id_material']
        tabladatos[:] = [item for item in tabladatos if item['id_material'] != int(id_material)]
        return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos)

    return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos)

@modulo_inventario.route('/inventario/productos',methods=["GET","POST"])
def productos():
    # productos = Producto.query.join(RecetaItem, Producto.id_producto == RecetaItem.productoid_itm).filter(Producto.estatus == 1 and RecetaItem.estatus == 1).all()
    consulta = text("""
    SELECT id_producto, nombre_producto, alias, dias_caducidadpd, costoproducto costoventa, ROUND(SUM(costo_mat) * cantidad, 2) costoproduccion,  CONCAT(ROUND(SUM(cantidad), 2), ' g') peso
    FROM producto p
        inner join recetaitem on productoid_itm = id_producto
        inner join material on materialid_itm = id_material
    WHERE p.estatus = 1 and recetaitem.estatus = 1
    GROUP BY nombre_producto, alias, dias_caducidadpd, costoproducto;
    """)
    productos = db.session.execute(consulta)
    return render_template('Inventarios/Producto/productos.html', productos=productos)

@modulo_inventario.route('/inventario/detalle', methods=["GET", "POST"])
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
        redirect(url_for('editarProducto', id_producto=id_producto))  # Mantén al usuario en la misma página
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
        return redirect(url_for('productos'))
    return render_template('Inventarios/Producto/modificarProducto.html', form=productoF, tabladatos=tabladatos, producto=producto)

@modulo_inventario.route('/inventario/eliminarIngrediente', methods=["POST"])
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
def paquetes():
    query =  text("""
    SELECT id_paquete, nombre_paq, costopaquete_paq, cantidadproductos_paq
    FROM paquete
    WHERE estatus = 1;
    """)
    paquete = db.session.execute(query)
    return render_template('Paquetes/paquetes.html', paquetes = paquete)

@modulo_inventario.route('/paquetes/detalle', methods=["GET", "POST"])
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
def inventariosAddPaquete():
    productosPaquete.clear()
    paqueteForm  = PaqueteForm(request.form)
    productos = Producto.query.all()
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteForm.productos.choices = opciones
    return render_template('Paquetes/agregarPaquete.html', form = paqueteForm, productosPaquete = productosPaquete)

@modulo_inventario.route('/paquetes/guardarPaquete', methods=["POST"])
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

            return redirect(url_for('paquetes'))
    else:
        return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete)

@modulo_inventario.route('/paquetes/editarPaquete', methods=["GET", "POST"])
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
            return redirect(url_for('paquetes'))

@modulo_inventario.route('/paquetes/eliminarProducto', methods=["POST"])
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
def eliminarPaquete():
    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)
    paquete.estatus = 0
    db.session.commit()
    paqueteitems = PaqueteItem.query.filter_by(paqueteid_itm=id_paquete).all()
    for item in paqueteitems:
        item.estatus = 0
        db.session.commit()
    

    return redirect(url_for('paquetes'))