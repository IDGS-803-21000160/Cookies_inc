from flask import  render_template, request, redirect, url_for, flash, current_app, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import text
from datetime import datetime
from flask_login import login_required,current_user

from Entities.Inventario import Usuario
from Entities.UsuarioForm import UserFormReg
from Entities.Inventario import db


modulo_usuarios=Blueprint('modulo_usuarios',__name__)


common_passwords = ['123456', 'password', '12345678', 'qwerty', '123456789']


@modulo_usuarios.route("/pagePrincipal/user", methods=["GET", "POST"])
@login_required
def user():
    print(current_user.id_usuario)
    user_formreg = UserFormReg(request.form)
    allUsuarios=Usuario.query.all()
    alert=''
    if request.method == 'POST':
        action = request.form.get('action')
        #Reguistro de Usuarios
        if request.form.get('registrar') and user_formreg.validate_on_submit():
            new_password = user_formreg.password.data
            new_username = user_formreg.username.data
            
            if new_password in common_passwords:
                flash('La contraseña utilizada es demasiado común. Por favor, elige otra.')
            
            if any(check_password_hash(u.password, new_password) for u in allUsuarios):
                alert='alert-danger'
                flash('La contraseña ya ha sido utilizada. Por favor, elige otra.')
            else:
                try:
                    newUser=Usuario(tipousuario=user_formreg.tipousuario.data,
                                nombrecompleto=user_formreg.nombrecompleto.data,
                                usuario_registro=current_user.id_usuario,
                                user = user_formreg.username.data,
                                password = generate_password_hash(user_formreg.password.data)
                                )
                    db.session.add(newUser)
                    db.session.commit()
                    alert='alert-success'
                    flash('Usuario Registrado Correctamente...')
                    user_formreg.nombrecompleto.data=''
                    user_formreg.username.data=''
                    user_formreg.password.data=''
                except Exception as e:
                    db.session.rollback()
                    print(f"Error al agregar el usuario: {e}")
        #Eliminar Usuarios
        elif action == 'eliminar':
            id=request.form.get('idUserDelete')
            print(id)
            user_to_delete=Usuario.query.get(id)
            if user_to_delete:
                user_to_delete.estatus=False
                print(user_to_delete.estatus)
                db.session.commit()
                
            else:
                print('Error')
        #Editar Usuarios
        elif action == 'editarS':
            id=request.form.get('idUserEdit')
            print(id)
            existing_user=Usuario.query.get(id)
            
            if existing_user:
                existing_user.nombrecompleto=user_formreg.nombrecompleto.data
                existing_user.tipousuario = user_formreg.tipousuario.data
                existing_user.user = user_formreg.username.data
                
                if user_formreg.password.data:
                    existing_user.password = generate_password_hash(user_formreg.password.data)
                
                existing_user.ultima_modificacion = datetime.now()
                
                db.session.commit()
                flash('Usuario Editado Correctamente...')
                #Se limpia el formulario
                user_formreg.nombrecompleto.data=''
                user_formreg.username.data=''
                user_formreg.password.data=''
            else:
                print('Fallo la modificacion')
            
            
    return render_template('Usuarios/usuarios.html', form=user_formreg,users=allUsuarios,alert=alert)