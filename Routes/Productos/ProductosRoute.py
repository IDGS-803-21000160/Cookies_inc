
from flask import  render_template, request, redirect, url_for, flash, Blueprint, jsonify
from sqlalchemy import text
from Entities.InventarioProductoForm import InventarioProductoForm
from Entities.Inventario import Material, RecetaItem, Inventario
from Entities.Inventario import Producto
from datetime import datetime
from flask_login import current_user

from Entities.InventarioMermaSalida import InventarioMerma, InventarioSalida
from Entities.Inventario import db


modulo_producto = Blueprint('modulo_producto', __name__)
 

tabladatos = []

@modulo_producto.route('/inventario/agregarProducto',methods=["GET","POST"])
def inventariosAddProducto():

    alerta = ''
    if request.args.get('alerta'):
        alerta = request.args.get('alerta')
    if alerta == '':
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
    return render_template('Inventarios/Producto/agregarProducto.html', form = productoForm, tabladatos = tabladatos, costoProduccion = 0, alerta = alerta)

@modulo_producto.route('/inventario/guardarProducto', methods=["POST"])
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
        
        cantidad = request.form.get("cantidad", type=float)
        merma = request.form.get("merma", type=float)

        if cantidad is None or merma is None:
            return redirect(url_for('modulo_producto.inventariosAddProducto', alerta = 'No has ingresado una cantidad o merma valida!' ))  # Mantén al usuario en la misma página

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
            redirect(url_for('modulo_producto.inventariosAddProducto', alerta = 'No has ingresado ingredientes para el producto!'))  # Mantén al usuario en la misma página
        else: 

            if productoF.nombreProducto.data == '' or productoF.alias.data == '' or productoF.costoProducto.data == '' or productoF.diasCaducidad.data == '':
                return redirect(url_for('modulo_producto.inventariosAddProducto', alerta = 'No has ingresado todos los campos requeridos!'))

            nuevo_producto = Producto(
                nombre_producto=productoF.nombreProducto.data,
                alias=productoF.alias.data,
                estatus=1,
                usuario_registro= current_user.id_usuario,
                fecha_registro=datetime.now(),
                costoproducto=productoF.costoProducto.data,
                dias_caducidadpd=productoF.diasCaducidad.data,
            )
            db.session.add(nuevo_producto)
            db.session.commit()

            if nuevo_producto.id_producto:
                id_producto = nuevo_producto.id_producto

                for item in tabladatos:
                    addItem = RecetaItem(
                        productoid_itm=id_producto,
                        materialid_itm=item['id_material'],
                        cantidad= float(item['cantidad']) / 50,
                        estatus=1,
                        usuario_registro= current_user.id_usuario,
                        fecha_registro=datetime.now(),
                        cantidad_merma = float(item['merma']) / 50
                    )
                    db.session.add(addItem)
                    db.session.commit()
                
                usuariop = current_user.id_usuario
                db.session.execute(
                        text("CALL entradaInventario(:tipo, :id_materia_producto, :cantidad, :usuariop)"),
                        {"tipo": 2, "id_materia_producto": id_producto, "cantidad": 0, "usuariop": usuariop}
                    )
                db.session.commit()

                tabladatos.clear()

                return redirect(url_for('modulo_producto.productos', success=True, alerta='Producto guardado correctamente!'))
            else:
               
                return redirect(url_for('modulo_producto.productos', success=False, alerta='Error al guardar el producto.'))

    elif request.form['action'] == 'quitar':
        # Lógica para quitar ingredientes de la lista
        id_material = request.form['id_material']
        tabladatos[:] = [item for item in tabladatos if item['id_material'] != int(id_material)]
        costoProduccion = round(sum([float(item['costo']) * (float(item['cantidad']) + float(item['merma'])) for item in tabladatos]), 2)
        return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos, costoProduccion = costoProduccion)

    return render_template('Inventarios/Producto/agregarProducto.html', form=productoF, tabladatos=tabladatos, costoProduccion = costoProduccion)

@modulo_producto.route('/inventario/productos',methods=["GET","POST"])
def productos():
    alerta = ''
    sucess = ''
    if request.args.get('alerta'):
        alerta = request.args.get('alerta')
        sucess = request.args.get('success')
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
    return render_template('Inventarios/Producto/productos.html', productos=productos, alerta = alerta, sucess = sucess)

@modulo_producto.route('/inventario/detalle', methods=["GET", "POST"])
def verReceta():
    tabladatos.clear()
    id_producto = request.form['id_producto']
    consulta = text("""
    SELECT nombre_producto, nombre_mat, cantidad * 50 cantidad, cantidad_merma * 50 cantidad_merma
    FROM recetaitem
    inner join material on id_material = materialid_itm
    inner join producto on id_producto = productoid_itm
    WHERE productoid_itm = :id_producto;
    """)
    resultados = db.session.execute(consulta.params(id_producto=id_producto))
    producto = Producto.query.get(id_producto)
    return render_template('Inventarios/Producto/detalleProducto.html', materiales=resultados, producto = producto)

@modulo_producto.route('/inventario/eliminarProducto', methods=["POST"])
def eliminarProducto():
    id_producto = request.form['id_producto']
    producto = Producto.query.get(id_producto)
    producto.estatus = 0
    db.session.commit()
    receta = RecetaItem.query.filter_by(productoid_itm=id_producto).all()
    for item in receta:
        item.estatus = 0
        db.session.commit()
    return redirect(url_for('modulo_producto.productos', success=True, alerta='Producto eliminado correctamente!'))

@modulo_producto.route('/inventario/editarProducto', methods=["GET", "POST"])
def editarProducto():

    alerta = ''
    id_producto = ''

    if request.args.get('alerta'):
        alerta = request.args.get('alerta')
    if request.args.get('id_producto'):
        id_producto = request.args.get('id_producto')
    else:
        id_producto = request.form['id_producto']

    tabladatos.clear()
    producto = Producto.query.get(id_producto)
    productoForm = InventarioProductoForm(request.form)
    ingredientes = Material.query.all()
    opciones = [(receta.id_material, receta.nombre_mat) for receta in ingredientes]
    productoForm.materiales.choices = opciones

    consulta = text("""
    SELECT nombre_producto, nombre_mat, cantidad, materialid_itm, cantidad_merma
    FROM recetaitem
    inner join material on id_material = materialid_itm
    inner join producto on id_producto = productoid_itm
    WHERE productoid_itm = :id_producto;
    """)
    ingredientes = db.session.execute(consulta.params(id_producto=id_producto))
    
    for item in ingredientes:
        tabladatos.append({"id_material": item.materialid_itm, "nombre_material": item.nombre_mat, "cantidad" : item.cantidad * 50, "merma" : item.cantidad_merma * 50})
    print(tabladatos)
    return render_template('Inventarios/Producto/modificarProducto.html', form=productoForm, producto=producto, tabladatos=tabladatos, alerta = alerta)

@modulo_producto.route('/inventario/actualizarProducto', methods=["POST"])
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
        merma = request.form.get("merma", type=int)

        if cantidad is None or merma is None:
            return redirect(url_for('modulo_producto.editarProducto', id_producto=id_producto, alerta = 'No has ingresado una cantidad o merma valida!' ))

        id_material = productoF.materiales.data
        nombre_material = next((nombre_mat for id_mat, nombre_mat in opciones if id_mat == id_material), None)
        if nombre_material and nombre_material not in [item['nombre_material'] for item in tabladatos]:
            tabladatos.append({"id_material": id_material, "nombre_material": nombre_material, "cantidad": cantidad, "merma" : merma})
        redirect(url_for('modulo_producto.editarProducto', id_producto=id_producto))  # Mantén al usuario en la misma página
        
        return render_template('Inventarios/Producto/modificarProducto.html', form=productoF, tabladatos=tabladatos, producto=producto)
    
    elif request.form['action'] == 'guardar_producto':

        if tabladatos == []:
            return redirect(url_for('modulo_producto.editarProducto', id_producto=id_producto, alerta = 'No has ingresado ingredientes para el producto!'))
        elif productoF.nombreProducto.data == '' or productoF.alias.data == '' or productoF.costoProducto.data == '' or productoF.diasCaducidad.data == '':
            return redirect(url_for('modulo_producto.editarProducto', id_producto=id_producto, alerta = 'No has ingresado todos los campos requeridos!'))

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
                cantidad=item['cantidad'] / 50,
                estatus=1,
                usuario_registro= current_user.id_usuario,
                fecha_registro=datetime.now(),
                cantidad_merma = item['merma'] / 50
            )
            db.session.add(addItem)
            db.session.commit()
        tabladatos.clear()

        return redirect(url_for('modulo_producto.productos', success=True, alerta='Producto actualizado correctamente!'))
    return render_template('Inventarios/Producto/modificarProducto.html', form=productoF, tabladatos=tabladatos, producto=producto)

@modulo_producto.route('/inventario/eliminarIngrediente', methods=["POST"])
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
