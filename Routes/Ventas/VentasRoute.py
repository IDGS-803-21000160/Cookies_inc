from flask import  render_template, request, redirect, url_for, flash, current_app, Blueprint,send_file
from flask_login import current_user,login_required
import random, json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io
import datetime



from sqlalchemy import text
from Entities.Inventario import VistaDetalleProducto,VistaDetallePaquete
from Entities.ClienteForm import ClienteFormReg
from Entities.Inventario import db

# entidades ventaCorte
from Entities.VentaCorte import VentaForm
from datetime import datetime, timedelta

modulo_ventas=Blueprint('modulo_ventas',__name__)

galletas=[]
idGalletas=[]
@modulo_ventas.route("/pagePrincipal/venta",methods=["GET", "POST"])
@login_required
def ventas():
    cliente_form=ClienteFormReg(request.form)
    productos=VistaDetalleProducto.query.all()
    paquete=VistaDetallePaquete.query.all()
    alert=''
    if request.method == 'POST':
        if request.form.get('registrar'):
            datos_producto = request.form['registrar']
            producto_id, nombre_galleta, precio_galleta = datos_producto.split('-', 2)
            
            cantidad_galletas = int(request.form[f'numero_{producto_id}'])
            costo_total = cantidad_galletas * float(precio_galleta)
            
            galletas.append((nombre_galleta,cantidad_galletas,costo_total) )
            for paq in paquete:
                print(paq.productos)
            
            # Definir la lista de diccionarios
            product = {"producto_id": int(producto_id), "cantidad": cantidad_galletas, "descuento":0.00}
                
            idGalletas.append(product)
            
        elif 'quitarProducto' in request.form:
            index_to_remove = int(request.form['quitarProducto'])
            if 0 <= index_to_remove < len(galletas):
                galletas.pop(index_to_remove)
                idGalletas.pop(index_to_remove)
                print('Producto eliminado', galletas)
                print(galletas)
                print(idGalletas)
                
        elif 'ingresar' in request.form and cliente_form.validate_on_submit():
            productos_ids = [producto['producto_id'] for producto in idGalletas]
            productos_disponibles = VistaDetalleProducto.query.filter(VistaDetalleProducto.idProducto.in_(productos_ids)).all()
            
            todo_disponible = True
            for producto_venta in idGalletas:
                producto_disponible = next((prod for prod in productos_disponibles if prod.idProducto == producto_venta["producto_id"]), None)
                
                if not producto_disponible or producto_venta["cantidad"] > producto_disponible.cantidad:
                    # Utilizar el nombre del producto en el mensaje
                    nombre_producto = producto_disponible.nombre_producto if producto_disponible else "Desconocido"
                    alert='alert-danger'
                    flash(f"Cantidad no disponible para el producto {nombre_producto}", "error")
                    todo_disponible = False
                    break

            if not todo_disponible:
                return render_template('Ventas/Ventas/ventaGalletas.html', productos=productos, galletas=galletas, form=cliente_form,alert=alert)
            
            if not galletas or not idGalletas:
                alert='alert-danger'
                flash("No hay productos seleccionados para la venta.", "error")
                return render_template('Ventas/Ventas/ventaGalletas.html', productos=productos, galletas=galletas, form=cliente_form,alert=alert)
            
            # Si todo está disponible, proceder con la venta
            try:
                nombre_cliente=cliente_form.nombreCliente.data
                correo=cliente_form.correo.data
                usuario_venta=current_user.id_usuario
                usuario_registro=current_user.id_usuario
                folio_venta = str(random.randint(1000000, 9999999)) 
                
                print(folio_venta)
                print(idGalletas)
                
                
                # Preparar la llamada al procedimiento almacenado
                sql = text(f"CALL GenerarVentaNuevaKev(:nombre_cliente, :correo, :usuario_venta, :folio_venta, :productos, :usuario_registro)")
        
                result = db.session.execute(sql, {
                    'nombre_cliente': nombre_cliente,
                    'correo': correo,
                    'usuario_venta': usuario_venta,
                    'folio_venta': folio_venta,
                    'productos': json.dumps(idGalletas),
                    'usuario_registro': usuario_registro
                })
                
                db.session.commit()
                
                print('Venta Realizada con Exito')
                
                # Inicializar un buffer y el objeto canvas
                buffer = io.BytesIO()
                width, height = letter  # Puedes ajustar esto para un tamaño más pequeño si es necesario
                c = canvas.Canvas(buffer, pagesize=(width / 2, height))  # Usar la mitad del ancho de una página carta para el ticket

                # Encabezado del ticket
                c.setFont("Helvetica-Bold", 12)
                c.drawString(30, height - 30, "Tinda de Galletas Cookies")
                c.setFont("Helvetica", 10)
                c.drawString(30, height - 50, "Dirección de la Empresa")
                c.drawString(30, height - 70, f"Fecha y Hora: { datetime.datetime.now()}")
                c.drawString(30, height - 90, f"Folio: {folio_venta}")


                # Datos para el ticket (encabezados y filas)
                encabezados = ['Producto', 'Cant.', 'Precio']
                datos_tabla = [encabezados] + galletas  # Asumiendo que `galletas` es una lista de tus productos

                # Crear y configurar la tabla
                table = Table(datos_tabla, colWidths=[150, 70, 50])  # Puedes ajustar las anchuras
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ]))

                # Dibujar la tabla en el ticket
                table.wrapOn(c, width / 2, height)
                table.drawOn(c, 30, height - 200)  # Ajusta la posición vertical según sea necesario

                # Finalizar el ticket
                c.save()
                
                # Preparar para la descarga
                buffer.seek(0)
                response= send_file(buffer, as_attachment=True, download_name=f"venta_{folio_venta}.pdf")

                galletas.clear()
                idGalletas.clear()
                cliente_form.nombreCliente.data = ''
                cliente_form.correo.data = ''

                alert='alert-success'
                flash("Venta realizada con Éxito...")
                return response
                
            except Exception as e:
                db.session.rollback()
                print(f"Error al agregar el usuario: {e}")
        
    
    return render_template('Ventas/Ventas/ventaGalletas.html',productos=productos,galletas=galletas,form=cliente_form,alert=alert)


paquetes=[]
galletasVent=[]
@modulo_ventas.route("/pagePrincipal/ventaPaquetes",methods=["GET", "POST"])
@login_required
def ventasPaq():
    cliente_form=ClienteFormReg(request.form)
    paquete=VistaDetallePaquete.query.all()
    if request.method == 'POST':
        if request.form.get('registrar'):
            datos_producto = request.form['registrar']
            producto_id, nombre_galleta, precio_galleta = datos_producto.split('-', 2)
    
            cantidad_galletas = int(request.form[f'numero_{producto_id}'])
            costo_total = cantidad_galletas * precio_galleta
        
            paquetes.append((nombre_galleta,cantidad_galletas,costo_total) )
            
                        
            paquete_seleccionado = VistaDetallePaquete.query.filter_by(id_paquete=producto_id).first()
            
            if paquete_seleccionado:
                galletasVent.extend(paquete_seleccionado.productos)              
            print(galletasVent)
        elif 'quitarProducto' in request.form:
                paquetes.clear()
                galletasVent.clear()
                print('Producto eliminado', paquetes)
                print(paquetes)
                print(galletasVent)
        elif 'ingresar' in request.form and cliente_form.validate_on_submit():
            productos_ids = [producto['producto_id'] for producto in galletasVent]
            productos_disponibles = VistaDetalleProducto.query.filter(VistaDetalleProducto.idProducto.in_(productos_ids)).all()
            
            todo_disponible = True
            for producto_venta in galletasVent:
                producto_disponible = next((prod for prod in productos_disponibles if prod.idProducto == producto_venta["producto_id"]), None)
                
                if not producto_disponible or producto_venta["cantidad"] > producto_disponible.cantidad:
                    # Utilizar el nombre del producto en el mensaje
                    nombre_producto = producto_disponible.nombre_producto if producto_disponible else "Desconocido"
                    alert='alert-danger'
                    flash(f"El paquete no cuenta con la cantidad no disponible del producto {nombre_producto}", "error")
                    todo_disponible = False
                    break

            if not todo_disponible:
                return render_template('Ventas/Ventaspaq/ventasPaquetes.html', productos=paquete, galletas=paquetes, form=cliente_form,alert=alert)
            
            if not paquetes or not galletasVent:
                alert='alert-danger'
                flash("No hay productos seleccionados para la venta.", "error")
                return render_template('Ventas/Ventaspaq/ventasPaquetes.html',productos=paquete,galletas=paquetes,form=cliente_form)
            
            try:
                nombre_cliente=cliente_form.nombreCliente.data
                correo=cliente_form.correo.data
                usuario_venta=current_user.id_usuario
                usuario_registro=current_user.id_usuario
                folio_venta = str(random.randint(1000000, 9999999)) 
                
                print(folio_venta)
                print(idGalletas)
                # Preparar la llamada al procedimiento almacenado
                sql = text(f"CALL GenerarVentaNuevaKev(:nombre_cliente, :correo, :usuario_venta, :folio_venta, :productos, :usuario_registro)")
        
                result = db.session.execute(sql, {
                    'nombre_cliente': nombre_cliente,
                    'correo': correo,
                    'usuario_venta': usuario_venta,
                    'folio_venta': folio_venta,
                    'productos': json.dumps(galletasVent),
                    'usuario_registro': usuario_registro
                })
                
                db.session.commit()
                print('Venta Realizada con Exito')
            except Exception as e:
                db.session.rollback()
                print(f"Error al agregar el usuario: {e}")
        
    
    return render_template('Ventas/Ventaspaq/ventasPaquetes.html',productos=paquete,galletas=paquetes,form=cliente_form)


#******************************************************************************************
#                ********************* VENTA - CORTE **************
#******************************************************************************************


@modulo_ventas.route('/pagePrincipal/venta/corte', methods=["POST", "GET"])
def ventaCorte():
    ventaForm = VentaForm(request.form)    
    if request.method == "POST":
        print(request.form)
        tipo_corte = request.form['tipo_corte']
        fecha_actual = datetime.now()
        if tipo_corte == 'dia_actual':
            fecha_limite = fecha_actual
            if fecha_limite:
                consulta = text("SELECT * FROM venta WHERE fecha_venta >= :fecha_limite and estatus = 1")
                resultado = db.session.execute(consulta, {'fecha_limite': fecha_limite})
                registros = resultado.fetchall()
            else:
                return 'Tipo de consulta no válido'
        elif tipo_corte == 'semanal':
            fecha_limite = fecha_actual - timedelta(days=7)
            if fecha_limite:
                consulta = text("SELECT * FROM venta WHERE fecha_venta >= :fecha_limite and estatus = 1")
                resultado = db.session.execute(consulta, {'fecha_limite': fecha_limite})
                registros = resultado.fetchall()
            else:
                return 'Tipo de consulta no válido'
        elif tipo_corte == 'mensual':
            fecha_limite = fecha_actual - timedelta(days=30)
            if fecha_limite:
                consulta = text("SELECT * FROM venta WHERE fecha_venta >= :fecha_limite and estatus = 1")
                resultado = db.session.execute(consulta, {'fecha_limite': fecha_limite})
                registros = resultado.fetchall()
            else:
                return 'Tipo de consulta no válido'
        elif tipo_corte == 'anual':
            fecha_limite = fecha_actual - timedelta(days=365)
            if fecha_limite:
                consulta = text("SELECT * FROM venta WHERE fecha_venta >= :fecha_limite and estatus = 1")
                resultado = db.session.execute(consulta, {'fecha_limite': fecha_limite})
                registros = resultado.fetchall()
            else:
                return 'Tipo de consulta no válido'
        
        total = 0
        for item in registros:
            total = total + float(item[7])
        
        
        return render_template('Ventas/VentaCorte/ventaCorte.html', form = ventaForm, registros = registros, total = total)
        
    return render_template('Ventas/VentaCorte/ventaCorte.html', form = ventaForm)
