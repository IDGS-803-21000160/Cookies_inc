
from flask import  render_template, request, redirect, url_for, flash, Blueprint
from sqlalchemy import text
from Entities.InventarioMaterialForm import InventarioMaterialForm
from Entities.Inventario import Material, Proveedor
from datetime import datetime
from Entities.Inventario import db
from flask_login import current_user

modulo_materiales = Blueprint('modulo_materiales', __name__)


@modulo_materiales.route('/inventario/materiales',methods=["GET","POST"])
def materiales():
    alerta = ''
    success = ''

    if request.args.get('alerta'):
        alerta = request.args.get('alerta')
        success = request.args.get('success')

    query =  text("""
    SELECT id_material, nombre_mat, dias_caducidad,
    CASE WHEN unidad_medida = 'g' THEN 'Kg' WHEN unidad_medida = 'ml' THEN 'Litro' ELSE unidad_medida END unidad_medida, 
    IF(unidad_medida in ('g', 'ml'), ROUND(costo_mat * 1000, 4), costo_mat) costo_mat, IFNULL(nombre, '') proveedor
    FROM material
        LEFT JOIN proveedor on id_proveedor = proveedorid_itm
    WHERE material.estatus = 1;
    """)
    materiales = db.session.execute(query)
    return render_template('Inventarios/Materiales/materiales.html', materiales=materiales, alerta=alerta, success=success)

@modulo_materiales.route('/inventario/agregarMaterial',methods=["GET","POST"])
def inventariosAddMaterial():
    materialForm  = InventarioMaterialForm(request.form)
    
    proveedores = Proveedor.query.filter_by(estatus=1).all()
    opciones = [(proveedor.id_proveedor, proveedor.nombre) for proveedor in proveedores]
    materialForm.proveedores.choices = opciones


    return render_template('Inventarios/Materiales/agregarMaterial.html', form = materialForm)

@modulo_materiales.route('/inventario/editarMaterial', methods=["GET", "POST"])
def editarMaterial():
    id_material = request.form['material_id']
    
    material = Material.query.get(id_material)

    print(material)
    materialForm = InventarioMaterialForm(request.form, obj=material)
    materialForm.unidadMedidaAgregar.data = material.unidad_medida

    proveedores = Proveedor.query.filter_by(estatus=1).all()
    opciones = [(proveedor.id_proveedor, proveedor.nombre) for proveedor in proveedores]
    materialForm.proveedores.choices = opciones
    materialForm.proveedores.data = material.proveedorid_itm

    if materialForm.unidadMedidaAgregar.data == 'g' or materialForm.unidadMedidaAgregar.data == 'ml':
        materialForm.costoMaterial.data = material.costo_mat * 1000
        material.costo_mat = material.costo_mat * 1000 
        if materialForm.unidadMedidaAgregar.data == 'g':
            materialForm.unidadMedidaAgregar.data = 'Kg'
        else :
            materialForm.unidadMedidaAgregar.data = 'Litro'
    return render_template('Inventarios/Materiales/modificarMaterial.html', form=materialForm, material=material)

@modulo_materiales.route('/inventario/guardarMaterial', methods=["POST"])
def inventariosGuardarMaterial():   
    materialF = InventarioMaterialForm(request.form)

    proveedores = Proveedor.query.filter_by(estatus=1).all()
    opciones = [(proveedor.id_proveedor, proveedor.nombre) for proveedor in proveedores]
    materialF.proveedores.choices = opciones

    if request.method == "POST" and materialF.validate():

        nombrematerial = materialF.nombreMaterial.data.upper()
        consulta = text("SELECT nombre_mat FROM material WHERE UPPER(nombre_mat) = :nombre_mat AND estatus = 1")
        material = db.session.execute(consulta, {'nombre_mat': nombrematerial}).fetchone()
        if material:
            return redirect(url_for('modulo_materiales.materiales', alerta = 'Material ya existe!', success = False))
        
        

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
        usuario_registro= current_user.id_usuario,  # Puedes establecer el usuario de registro aquí si es necesario
        fecha_registro=datetime.now(),  # Puedes establecer la fecha de registro aquí si es necesario,
        proveedorid_itm=materialF.proveedores.data
        )
        db.session.add(nuevo_material)
        db.session.commit()
        
        return redirect(url_for('modulo_materiales.materiales', alerta = 'Material Añadido Correctamente!', success = True))  # Redirige a donde quieras después de guardar el material
    
    return render_template('Inventarios/Materiales/agregarMaterial.html', form=materialF)

@modulo_materiales.route('/inventario/eliminarMaterial', methods=["POST"])
def eliminarMaterial():
    id_material = request.form['material_id']
    material = Material.query.get(id_material)
    material.estatus = 0
    db.session.commit()
    return redirect(url_for('modulo_materiales.materiales', alerta = 'Material Eliminado Correctamente!', success = True))

@modulo_materiales.route('/inventario/actualizarMaterial', methods=["POST"])
def actualizarMaterial():
    id_material = request.form['material_id']
    material = Material.query.get(id_material)
    materialForm = InventarioMaterialForm(request.form)

    proveedor = Proveedor.query.filter_by(id_proveedor=material.proveedorid_itm).first()
    proveedores = Proveedor.query.filter_by(estatus=1).all()
    opciones = [(proveedor.id_proveedor, proveedor.nombre) for proveedor in proveedores]
    materialForm.proveedores.choices = opciones


    if request.method == "POST" and materialForm.validate():

        nombrematerial = materialForm.nombreMaterial.data.upper()
        consulta = text("SELECT nombre_mat FROM material WHERE UPPER(nombre_mat) = :nombre_mat AND estatus = 1 and id_material != :id_material")
        materialexiste = db.session.execute(consulta, {'nombre_mat': nombrematerial, 'id_material' : id_material}).fetchone()
        if materialexiste:
            return redirect(url_for('modulo_materiales.materiales', alerta = 'Material ya existe!', success = False))

        costomaterial = float(materialForm.costoMaterial.data)
        unidad = materialForm.unidadMedidaAgregar.data

        if materialForm.unidadMedidaAgregar.data == 'Kg' or materialForm.unidadMedidaAgregar.data == 'Litro':
            costomaterial = costomaterial / 1000
            if materialForm.unidadMedidaAgregar.data == 'Kg':
                unidad = 'g'
            else:
                unidad = 'ml'
        Material 
        material.nombre_mat = materialForm.nombreMaterial.data
        material.dias_caducidad = materialForm.diasCaducidad.data
        material.unidad_medida = unidad
        material.costo_mat = costomaterial
        material.proveedorid_itm = materialForm.proveedores.data
        db.session.commit()
        return redirect(url_for('modulo_materiales.materiales', alerta = 'Material Actualizado Correctamente!', success = True))
    return render_template('Inventarios/Materiales/modificarMaterial.html', form=materialForm, material=material)
