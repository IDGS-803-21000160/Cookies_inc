
from flask import  render_template, request, redirect, url_for, flash, Blueprint
from sqlalchemy import text
from Entities.Inventario import Paquete, PaqueteItem
from Entities.Inventario import Producto
from Entities.PaqueteForm import PaqueteForm
from datetime import datetime
from flask_login import current_user

from Entities.InventarioMermaSalida import InventarioMerma, InventarioSalida
from Entities.Inventario import db
from permissions import pos_required
from flask_login import login_required,current_user


modulo_paquetes = Blueprint('modulo_paquetes', __name__)

productosPaquete = []
  
@modulo_paquetes.route('/paquetes')
@login_required
@pos_required
def paquetes():

    alerta = ''
    success = ''
    if request.args.get('alerta'):
        alerta = request.args.get('alerta')
        sucess = request.args.get('success')

    query =  text("""
    SELECT id_paquete, nombre_paq, costopaquete_paq, cantidadproductos_paq
    FROM paquete
    WHERE estatus = 1;
    """)
    paquete = db.session.execute(query)
    return render_template('Paquetes/paquetes.html', paquetes = paquete, alerta = alerta, success = success)

@modulo_paquetes.route('/paquetes/detalle', methods=["GET", "POST"])
def verDetalle():
    id_paquete = request.form['id_paquete']
    consulta = text("""
    SELECT nombre_producto nombreproducto, alias, costoproducto costoventa, CONCAT(ROUND(SUM(IFNULL(cantidad, 0)), 2), ' g') peso, cantidadproducto_itm cantidad
    FROM paqueteitem
        INNER JOIN producto on id_producto = productoid_itm
        LEFT JOIN recetaitem on id_producto = recetaitem.productoid_itm
        LEFT JOIN material on id_material = materialid_itm
    WHERE paqueteid_itm = :id_paquete
    GROUP BY  nombre_producto, alias, costoproducto, cantidadproducto_itm;
    """)
    resultados = db.session.execute(consulta.params(id_paquete=id_paquete))
    paquete = Paquete.query.get(id_paquete)
    return render_template('Paquetes/paquetesDetalle.html', productos=resultados, paquete = paquete)

@modulo_paquetes.route('/paquetes/agregarPaquete',methods=["GET","POST"])
def inventariosAddPaquete():

    alerta = ''

    if request.args.get('alerta'):
        alerta = request.args.get('alerta')

    productosPaquete.clear()
    paqueteForm  = PaqueteForm(request.form)
    consulta = text("""
    SELECT id_producto, CONCAT( nombre_producto, '  |     peso de    ',  ROUND(SUM(cantidad), 3), '  g', '     | costo de    $', costoproducto ) nombre_producto
    FROM producto
        inner join recetaitem on id_producto = productoid_itm
        inner join material on id_material = materialid_itm
    where producto.estatus = 1 and recetaitem.estatus = 1
    group by id_producto, nombre_producto;
    """)
    productos = db.session.execute(consulta)
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteForm.productos.choices = opciones
    return render_template('Paquetes/agregarPaquete.html', form = paqueteForm, productosPaquete = productosPaquete, precio = 0, peso = 0, alerta = alerta)

@modulo_paquetes.route('/paquetes/guardarPaquete', methods=["POST", "GET"])
def inventariosGuardarPaquete():
    paqueteF = PaqueteForm(request.form)
    consulta = text("""
    SELECT id_producto, CONCAT( nombre_producto, '  |     peso de    ',  ROUND(SUM(cantidad), 3), '  g', '     | costo de    $', costoproducto ) nombre_producto
    FROM producto
        inner join recetaitem on id_producto = productoid_itm
        inner join material on id_material = materialid_itm
    where producto.estatus = 1 and recetaitem.estatus = 1
    group by id_producto, nombre_producto;
    """)
    productos = db.session.execute(consulta)
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteF.productos.choices = opciones

    precioSugerido = 0
    pesoTotal = 0

    if productosPaquete != []:
        precioSugerido = sum([item['costo'] for item in productosPaquete])
        pesoTotal = sum([item['peso'] for item in productosPaquete])

    # Verifica qué botón se presionó
    if request.form['action'] == 'agregar_item':
        # Lógica para agregar ingredientes a la lista
        cantidad = request.form.get("cantidad", type=int)

        if cantidad == None:
            precioSugerido = round(sum([float(item['costo']) for item in productosPaquete]), 3)
            pesoTotal = round( sum( [ float(item['peso']) for item in productosPaquete ] ), 3 )
            return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, alerta = 'La cantidad debe ser mayor a 0', precio = precioSugerido, peso = pesoTotal)

        elif cantidad <= 0:
            precioSugerido = round(sum([float(item['costo']) for item in productosPaquete]), 3)
            pesoTotal = round( sum( [ float(item['peso']) for item in productosPaquete ] ), 3 )
            return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, alerta = 'La cantidad debe ser mayor a 0', precio = precioSugerido, peso = pesoTotal)

        id_producto = paqueteF.productos.data
        nombre_producto = next((nombre_producto for id_pd, nombre_producto in opciones if id_pd == id_producto), None)
        
        if nombre_producto and nombre_producto not in [item['nombre_producto'] for item in productosPaquete]:

            consulta2 = text("""
            SELECT ROUND(SUM(cantidad), 3) as peso, producto.costoproducto
            FROM producto
                inner join recetaitem on id_producto = productoid_itm
                inner join material on id_material = materialid_itm
            where producto.estatus = 1 and id_producto = :id_producto
            group by id_producto, nombre_producto;
            """)
            precioPeso = db.session.execute(consulta2.params(id_producto=id_producto)).fetchone()
            
            productosPaquete.append({"id_producto": id_producto, "nombre_producto": nombre_producto, "cantidad": cantidad, "costo" : precioPeso.costoproducto * cantidad, "peso" : precioPeso.peso * cantidad})
            
            precioSugerido = round(sum([float(item['costo']) for item in productosPaquete]), 3)
            pesoTotal = round( sum( [ float(item['peso']) for item in productosPaquete ] ), 3 )   

        return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, precio = precioSugerido, peso = pesoTotal)
    
    elif request.form['action'] == 'guardar_paquete':

        if productosPaquete == []:
            return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, alerta = 'Debe agregar al menos un producto al paquete', precio = precioSugerido, peso = pesoTotal)
        elif paqueteF.nombrePaquete.data == '' or paqueteF.costoPaquete.data == '':
            return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, alerta = 'Debe llenar todos los campos', precio = precioSugerido, peso = pesoTotal)
        else: 
            nuevo_paquete = Paquete(
                nombre_paq=paqueteF.nombrePaquete.data,
                costopaquete_paq=paqueteF.costoPaquete.data,
                cantidadproductos_paq=len(productosPaquete),
                estatus=1,
                usuarioregistro = current_user.id_usuario,
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
                    usuarioregistro= current_user.id_usuario,
                    fecha_registro=datetime.now()
                )
                db.session.add(addItem)
                db.session.commit()
            productosPaquete.clear()

            return redirect(url_for('modulo_paquetes.paquetes', success = True, alerta = 'Paquete Añadido Correctamente!'))
        
    elif request.form['action'] == 'quitar':
        id_producto = request.form['id_producto']
        productosPaquete[:] = [item for item in productosPaquete if item['id_producto'] != int(id_producto)]
        precioSugerido = round(sum([item['costo'] for item in productosPaquete]), 3)
        pesoTotal = round( sum( [ float(item['peso']) for item in productosPaquete ] ), 3 )
        return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, precio = precioSugerido, peso = pesoTotal)
    return render_template('Paquetes/agregarPaquete.html', form=paqueteF, productosPaquete=productosPaquete)

@modulo_paquetes.route('/paquetes/editarPaquete', methods=["GET", "POST"])
def editarPaquete():
    productosPaquete.clear()
    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)
    paqueteForm = PaqueteForm(request.form)
    consulta = text("""
    SELECT id_producto, CONCAT( nombre_producto, '  |     peso de    ',  ROUND(SUM(cantidad), 3), '  g', '     | costo de    $', costoproducto ) nombre_producto
    FROM producto
        inner join recetaitem on id_producto = productoid_itm
        inner join material on id_material = materialid_itm
    where producto.estatus = 1 and recetaitem.estatus = 1
    group by id_producto, nombre_producto;
    """)
    productos = db.session.execute(consulta)
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteForm.productos.choices = opciones

    consulta = text("""
    SELECT pq.productoid_itm, nombre_producto, ROUND(SUM(cantidad), 3) as peso, 
    ROUND(p.costoproducto * cantidadproducto_itm, 3) costoSugerido, cantidadproducto_itm cantidad
    FROM paquete
        INNER JOIN paqueteitem pq on pq.paqueteid_itm = paquete.id_paquete
        INNER JOIN producto p on id_producto = pq.productoid_itm
        INNER JOIN recetaitem r on p.id_producto = r.productoid_itm
        INNER JOIN material m on m.id_material = r.materialid_itm
    WHERE paqueteid_itm = 1
    GROUP BY pq.productoid_itm, nombre_producto;
    """)
    ingredientes = db.session.execute(consulta.params(id_paquete=id_paquete))

    for item in ingredientes:
        productosPaquete.append({"id_producto": item.productoid_itm, "nombre_producto": item.nombre_producto, "cantidad" : item.cantidad, "costo" : item.costoSugerido, "peso" : item.peso})
    precioSugerido = round(sum([float(item['costo']) for item in productosPaquete]), 3)
    pesoTotal = round( sum( [ float(item['peso']) for item in productosPaquete ] ), 3 )
    return render_template('Paquetes/modificarPaquete.html', form=paqueteForm, paquete=paquete, productosPaquete=productosPaquete, precio = precioSugerido, peso = pesoTotal)

@modulo_paquetes.route('/paquetes/actualizarPaquete', methods=["POST"])
def actualizarPaquete():
    paqueteF = PaqueteForm(request.form)
    consulta = text("""
    SELECT id_producto, CONCAT( nombre_producto, '  |     peso de    ',  ROUND(SUM(cantidad), 3), '  g', '     | costo de    $', costoproducto ) nombre_producto
    FROM producto
        inner join recetaitem on id_producto = productoid_itm
        inner join material on id_material = materialid_itm
    where producto.estatus = 1 and recetaitem.estatus = 1
    group by id_producto, nombre_producto;
    """)
    productos = db.session.execute(consulta)
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteF.productos.choices = opciones

    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)

    pesoTotal = 0
    precioSugerido = 0

    # Verifica qué botón se presionó
    precioSugerido = round(sum([float(item['costo']) for item in productosPaquete]), 3)
    pesoTotal = round( sum( [ float(item['peso']) for item in productosPaquete ] ), 3 )  
    
    if request.form['action'] == 'agregar_item':
        # Lógica para agregar ingredientes a la lista
        cantidad = request.form.get("cantidad", type=int)

        if cantidad == None:
            return render_template('Paquetes/modificarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, paquete=paquete, alerta = 'Ingresa una cantidad valida', success = 'False', precio = precioSugerido, peso = pesoTotal)
        
        elif cantidad <= 0:
            return render_template('Paquetes/modificarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, paquete=paquete, alerta = 'La cantidad debe ser mayor a 0', success = 'False', precio = precioSugerido, peso = pesoTotal)

        id_producto = paqueteF.productos.data
        nombre_producto = next((nombre_pd for id_pd, nombre_pd in opciones if id_pd == id_producto), None)
        if nombre_producto and nombre_producto not in [item['nombre_producto'] for item in productosPaquete]:
            consulta2 = text("""
            SELECT ROUND(SUM(cantidad), 3) as peso, producto.costoproducto
            FROM producto
                inner join recetaitem on id_producto = productoid_itm
                inner join material on id_material = materialid_itm
            where producto.estatus = 1 and id_producto = :id_producto
            group by id_producto, nombre_producto;
            """)
            precioPeso = db.session.execute(consulta2.params(id_producto=id_producto)).fetchone()
            productosPaquete.append({"id_producto": id_producto, "nombre_producto": nombre_producto, "cantidad": cantidad, "costo" : precioPeso.costoproducto * cantidad, "peso" : precioPeso.peso * cantidad})
            precioSugerido = round(sum([float(item['costo']) for item in productosPaquete]), 3)
            pesoTotal = round( sum( [ float(item['peso']) for item in productosPaquete ] ), 3 )  
        return render_template('Paquetes/modificarPaquete.html', form=paqueteF, productosPaquete=productosPaquete, paquete=paquete, precio = precioSugerido, peso = pesoTotal)
    
    elif request.form['action'] == 'guardar_paquete':
        # Lógica para guardar el producto completo
        if productosPaquete == []:
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
                    usuarioregistro= current_user.id_usuario,
                    fecha_registro=datetime.now()
                )
                db.session.add(addItem)
                db.session.commit()
            productosPaquete.clear()

            return redirect(url_for('modulo_paquetes.paquetes', success = True, alerta = 'Paquete Modificado Correctamente!'))

@modulo_paquetes.route('/paquetes/eliminarProducto', methods=["POST"])
def eliminarProductoPaquete():
    id_producto = request.form['id_producto']
    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)
    paqueteForm  = PaqueteForm(request.form)
    productos = Producto.query.all()
    opciones = [(producto.id_producto, producto.nombre_producto) for producto in productos]
    paqueteForm.productos.choices = opciones
    productosPaquete[:] = [item for item in productosPaquete if item['id_producto'] != int(id_producto)]
    precioSugerido = round(sum([float(item['costo']) for item in productosPaquete]), 3)
    pesoTotal = round( sum( [ float(item['peso']) for item in productosPaquete ] ), 3 )  
    return render_template('Paquetes/modificarPaquete.html', form=paqueteForm, productosPaquete=productosPaquete, paquete=paquete, precio = precioSugerido, peso = pesoTotal)

@modulo_paquetes.route('/paquetes/eliminarPaquete', methods=["POST"])
def eliminarPaquete():
    id_paquete = request.form['id_paquete']
    paquete = Paquete.query.get(id_paquete)
    paquete.estatus = 0
    db.session.commit()
    paqueteitems = PaqueteItem.query.filter_by(paqueteid_itm=id_paquete).all()
    for item in paqueteitems:
        item.estatus = 0
        db.session.commit()
    

    return redirect(url_for('modulo_paquetes.paquetes', success = True, alerta = 'Paquete Eliminado Correctamente!'))