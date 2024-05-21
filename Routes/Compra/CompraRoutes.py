from flask import  render_template, request, Blueprint, flash
from sqlalchemy import text
from Entities.Inventario import db, Proveedor, Compra, CompraItem, Material
from sqlalchemy import text
from flask_wtf.csrf import CSRFProtect
from Entities.CompraForm import CompraForm
from datetime import datetime, timedelta
from permissions import inventario_required
from flask_login import login_required,current_user


modulo_compras = Blueprint('modulo_compras', __name__)
csrf=CSRFProtect()


listaCompra_insertar = []
subtotal = 0
productos = []
@modulo_compras.route('/compra', methods=["GET","POST"])
@inventario_required
@login_required
def compra():
    global subtotal
    global listaCompra_insertar
    global productos
    
    total = 0
    compras = []
    listaProveedor = []
    ventaForm = CompraForm()
        
    compras = loadComprasRealizadas()
    
    if request.method == "GET":
        compras = loadComprasRealizadas()
    
        
    proveedores = Proveedor.query.filter_by(estatus='1').all()

    opcionesMateriales = [(prov.id_proveedor, prov.nombre) for prov in proveedores]
    ventaForm.tipo_prov.choices = opcionesMateriales

    for proveedor in proveedores:
        #print(proveedor.id_proveedor, proveedor.nombre, proveedor.telefono, proveedor.correo, proveedor.dias_visita, proveedor.estatus, proveedor.usuario_registro, proveedor.fecha_registro)
        listaProveedor.append({
            "id_proveedor": proveedor.id_proveedor,
            "nombre": proveedor.nombre
        })

    
    if request.method == "POST":   
        # print(request.form)
        id_proveedor = request.form['tipo_prov']
        if 'cargar' in request.form:
            productos = cargarProducto(id_proveedor) 
        elif 'Agregar' in request.form :
            print('Boton Agregar')
            print(request.form)
            listaCompra = []
            index = 0
            for i in productos :
                index = index + 1
                valor = int(request.form[f'cantidad_producto_{index}'])
                
                if valor > 0 :                    
                    if request.form[f'unidad_medida_{index}'] == 'pieza':
                        subtotal = float(valor) * float(i['costo'])
                        listaCompra.append({
                            'id_material': i['id_material'],
                            'nombre_producto': request.form[f'nombre_producto_{index}'],
                            'unidad_medida': request.form[f'unidad_medida_{index}'],
                            'cantidad_producto': valor,
                            'subtotal': subtotal
                        })
                    else:
                        subtotal = (float(valor) * 1000) * float(i['costo'])
                        listaCompra.append({
                            'id_material': i['id_material'],
                            'nombre_producto': request.form[f'nombre_producto_{index}'],
                            'unidad_medida': request.form[f'unidad_medida_{index}'],
                            'cantidad_producto': valor*1000,
                            'subtotal': round(subtotal, 2)
                        })
                elif valor < 0:
                    flash("ingresa un valor valido", "danger")
                
                
            total = round(total, 2)
            listaCompra_insertar.extend(listaCompra)
            
            for i in listaCompra_insertar:
                total = total + float(i['subtotal'])
                
            listaCompra = []
            
            return render_template('Compra/compra.html', prodct = productos, form = ventaForm, listaCompra = listaCompra_insertar, total = total, compra = compras)
        
        elif 'Eliminar' in request.form :
            
            index_eliminar = int(request.form['Eliminar'])
            listaCompra_insertar.pop(index_eliminar)
                #print('Elemento eliminado:', elemento_eliminado)
            for i in listaCompra_insertar:
                total = total + float(i['subtotal'])
            
            return render_template('Compra/compra.html', prodct = productos, form = ventaForm, listaCompra = listaCompra_insertar, total = total, compra = compras)
            
        elif 'Terminar' in request.form:    
            print('boton Terminar')
            # Armar folio
            fecha_hora_actual = datetime.now()
            ano_actual = str(fecha_hora_actual.year)
            minuto_actual = str(fecha_hora_actual.minute)
            segundo_actual = str(fecha_hora_actual.second)

            folio = f"{id_proveedor}-{segundo_actual}{minuto_actual}{ano_actual}"
            for i in listaCompra_insertar:
                total = total + float(i['subtotal'])
            print(total)
            
            try:
                nueva_compra = Compra(
                    proveedorid_comp = id_proveedor,  
                    usuario_comp = current_user.id_usuario,  
                    folio_comp = folio,  
                    fecha_comp = datetime.now(),  
                    cantidad = len(listaCompra_insertar),  
                    total = total, 
                    estatus = 1,  
                    fecha_registro=datetime.now()
                )
                
                db.session.add(nueva_compra)

                db.session.commit()
                
                # Obtener el último ID insertado (ID de la nueva compra)
                ultimo_id_insertado = nueva_compra.id_compra

                # Imprimir el último ID insertado para verificar
                print("Último ID insertado:", ultimo_id_insertado)
                print(listaCompra_insertar)
                for prod in listaCompra_insertar:
                    nuevo_product = CompraItem(
                        compra_itm = ultimo_id_insertado,
                        materialid_itm = prod['id_material'],
                        cantidad = prod['cantidad_producto'],
                        subtotal = prod['subtotal'],
                        estatus = 1,
                        usuario_registro = current_user.id_usuario,
                        fecha_registro = datetime.now()
                    )
                    
                    db.session.add(nuevo_product)

                    db.session.commit()   
                    
                consulta = text('CALL descuentoInventarioPorCompra(:parametro1)')
                db.session.execute(consulta, {'parametro1': ultimo_id_insertado})
                
                db.session.commit()
                
                flash("Compra realizada", "success")
            except:
                flash("Algo salio mal, intenta de nuevo", "danger")
            # for row in resultado:
            #     print(row)
                
            compras = loadComprasRealizadas()    
            
            productos_a_comprar = 0
            subtotal = 0
            total = 0
            index = 0
            listaCompra_insertar = []
            
    return render_template('Compra/compra.html', prodct = productos, form = ventaForm, listaCompra = listaCompra_insertar, total = total, compra = compras)


def cargarProducto(proveedor_id_deseado):
    productos = []

    query = """
            SELECT*FROM material WHERE proveedorid_itm = :idProveedor;
        """

    data = db.session.execute(text(query), {"idProveedor": proveedor_id_deseado})

    for material in data:
        #print(material.id_material, material.nombre_mat, material.costo_mat)
        productos.append({
            'id_material': material.id_material,
            'nombre': material.nombre_mat,
            'costo': material.costo_mat,
            'unidad_medida': material.unidad_medida
        })
    print(productos)
    return productos

def loadComprasRealizadas():
    compras = []

    materiales = db.session.query(Compra).all()

    for material in materiales:
        # print(material.id_compra, material.proveedorid_comp, material.usuario_comp)
        compras.append({
            'id_compra': material.id_compra,
            'proveedorid_comp': material.proveedorid_comp,
            'usuario_comp': material.usuario_comp,
            'folio_comp': material.folio_comp,
            'fecha_comp':material.fecha_comp,
            'cantidad_productos':material.cantidad,
            'total_compra': material.total
        })
        
    return compras

@modulo_compras.route('/detalleCompra', methods=["POST"])
@inventario_required
@login_required
def verDetalleCompra():
    if request.method == "POST":
        idCompra = int(request.form["idcompra"])
        query = """
            SELECT 
                c.id_compra,
                p.nombre,
                p.telefono,
                u.tipousuario,
                u.nombrecompleto,
                c.fecha_comp,
                c.cantidad,
                COUNT(1) AS cantProducto,
                GROUP_CONCAT('Nombre Mat: ',m.nombre_mat,' - Cantidad: ', ct.cantidad,
                    CASE
                        WHEN m.unidad_medida = 'g' or m.unidad_medida = 'ml'  THEN CONCAT(' - Precio $', (m.costo_mat * 1000))
                        ELSE CONCAT(' - Precio $', m.costo_mat)
                    END
                SEPARATOR ' | ') AS nomProducto,
                c.total
            FROM compra c
            LEFT JOIN compraitem ct ON c.id_compra = ct.compra_itm
            LEFT JOIN material m ON ct.materialid_itm = m.id_material
            LEFT JOIN proveedor p ON p.id_proveedor = c.proveedorid_comp
            LEFT JOIN usuario u ON u.id_usuario = c.usuario_comp
            WHERE c.id_compra = :idCompra
            GROUP BY c.id_compra;
        """

        data = db.session.execute(text(query), {"idCompra": idCompra})
        
        for row in data:
            id_compra = row.id_compra
            nombre_proveedor = row.nombre
            telefono_proveedor = row.telefono
            tipo_usuario = row.tipousuario
            nombre_usuario = row.nombrecompleto
            fecha_compra = row.fecha_comp
            cantidad = row.cantidad
            nombres_productos = row.nomProducto
            total = row.total

            datelleVenta = {
                'id_compra': id_compra,
                'nombre_proveedor': nombre_proveedor,
                'telefono_proveedor': telefono_proveedor,
                'tipo_usuario': tipo_usuario,
                'nombre_usuario': nombre_usuario,
                'fecha_compra': fecha_compra,
                'cantidad': cantidad,
                'nombres_productos': nombres_productos,
                'total': total
            }
            # print(f"ID Compra: {id_compra}")
            # print(f"Proveedor: {nombre_proveedor} - Teléfono: {telefono_proveedor}")
            # print(f"Tipo de usuario: {tipo_usuario} - Nombre: {nombre_usuario}")
            # print(f"Fecha de compra: {fecha_compra}")
            # print(f"Cantidad de productos: {cantidad} - Total productos: {cantidad_productos}")
            # print(f"Productos comprados: {nombres_productos}")
            # print("=" * 20)  # Separador entre cada fila
    
    return render_template("Compra/detalleCompra.html", compradetalle = datelleVenta)