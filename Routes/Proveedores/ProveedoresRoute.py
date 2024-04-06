from flask import  render_template, request, redirect, url_for, flash, current_app, Blueprint
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,login_user,logout_user,login_required,current_user

from Entities.Inventario import Proveedor
from Entities.ProveedorForm import ProveedorFormReg
from Entities.Inventario import db



moodulo_proveedor=Blueprint('moodulo_proveedor',__name__)

@moodulo_proveedor.route("/pagePrincipal/proveedor", methods=["GET", "POST"])
@login_required
def proveedor():
    provee_formreg = ProveedorFormReg(request.form)
    allProveedores=Proveedor.query.all()
    if request.method == 'POST':
        action = request.form.get('action')
        if request.form.get('registrar') and provee_formreg.validate_on_submit():
            try:
                newProveedor=Proveedor(nombre=provee_formreg.nombre.data,
                            telefono=provee_formreg.telefono.data,
                            usuario_registro=request.form.get('idUser'),
                            correo = provee_formreg.correo.data,
                            dias_visita = provee_formreg.dias_visita.data
                            )
                db.session.add(newProveedor)
                db.session.commit()
                flash('Usuario Registrado Correctamente...')
                provee_formreg.nombre.data=''
                provee_formreg.telefono.data=0
                provee_formreg.correo.data=''
                provee_formreg.dias_visita.data=''
                
            except Exception as e:
                db.session.rollback()
                print(f"Error al agregar el usuario: {e}")
            print('Yo soy quien reguistra')
        
        elif action == 'editarProv':
            id=request.form.get('idProvEdit')
            print('Yo soy quien edita')
            print(id)
            existing_prov=Proveedor.query.get(id)
            
            if existing_prov:
                existing_prov.nombre=provee_formreg.nombre.data
                existing_prov.telefono=provee_formreg.telefono.data
                existing_prov.correo=provee_formreg.correo.data
                existing_prov.dias_visita=provee_formreg.dias_visita.data
                
                db.session.commit()
                flash('Proveedor Editado Correctamente...')
                provee_formreg.nombre.data=''
                provee_formreg.correo.data=''
                provee_formreg.dias_visita.data=''
            else:
                print('Fallo la edición')
        
        elif request.form.get('eliminar'):
            print('Yo soy quien elimina')
    
    
    return render_template('Proveedores/proveedores.html',form=provee_formreg,proveedores=allProveedores)
