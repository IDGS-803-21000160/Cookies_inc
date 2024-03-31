from flask import Flask, render_template, request, jsonify, flash, redirect, session,url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import Flask
from flask_cors import CORS, cross_origin
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import forms
from datetime import datetime
from models import Usuario,Proveedor,LoginLog,VistaDetalleProducto
from models import db
from flask_login import LoginManager,login_user,logout_user,login_required,current_user


from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()
app.secret_key='esta es la clave secreta'

# Inicializa la extensión Admin
admin = Admin(app, name='MiAppAdmin', template_mode='bootstrap3', url='/panel_admin')
# Añade vistas al panel administrativo
admin.add_view(ModelView(Usuario, db.session))

login_manager_app=LoginManager(app)

#BLOQUEAR TODOS LOS ORIGENES
#CORS(app, resources={r"/*": {"origins": ""}})

#DESBLOQUEAR TODOS LOS ORIGENES
#CORS(app, resources={r"/*": {"origins": "*"}})

# DESBLOQUEAR CIERTOS ORIGENES
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5000"]}})
#CORS(app, resources={r"/*": {"origins": ["http://192.168.111.246.*", "http://192.168.111.86:8080","http://192.168.111.127.*"]}})

#--------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400


@app.errorhandler(401)
def bad_request(e):
    return render_template('401.html'), 400

@login_manager_app.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.tipousuario == 'ejecVentas':
            return f(*args, **kwargs)
        else:
            flash('Acceso denegado. Se requiere rol de administrador.')
            return redirect(url_for('index'))
    return decorated_function

#Función del Login
@app.route('/', methods=["GET", "POST"])
def index():
    user_form = forms.UsersForm(request.form)
    if request.method == 'POST' and user_form.validate_on_submit():
        username = user_form.username.data
        password = user_form.password.data

        user = Usuario.query.filter_by(user=username).first()
        ip_address=request.remote_addr
        user_agent=request.user_agent.string
        
        def log_attempt(user_id, successful):
            log = LoginLog(
                id_us=user_id,
                user=username,
                ip_address=ip_address,
                user_agent=user_agent,
                login_successful=successful
            )
            db.session.add(log)
            db.session.commit()

        # Verifica si el usuario existe
        if user:
            user_id = user.id_us
            # Verifica el estado del usuario
            if user.estatus == '0':
                log_attempt(user_id, False)
                flash('Usuario bloqueado.')
                return render_template("index.html", form=user_form)
            
            # Verifica la contraseña y el estatus del usuario
            if check_password_hash(user.password, password):
                if user.estatus == '1':
                    user.failed_attempts = 0  # Reinicia el contador de intentos fallidos tras un inicio de sesión exitoso
                    log_attempt(user_id, True)
                    db.session.commit()
                    login_user(user)
                    return redirect(url_for('pagePrincipal'))
            else:
                user.failed_attempts += 1  # Aumenta el contador de intentos fallidos
                log_attempt(user_id, False)
                if user.failed_attempts >= 3:
                    user.estatus = '0'
                    user.failed_attempts = 0  # Opcional: resetear el contador tras bloquear al usuario
                    db.session.commit()
                    flash('Usuario bloqueado por intentos fallidos de inicio de sesión.')
                else:
                    db.session.commit()
                    flash('Usuario o contraseña incorrectos.')
                    print(user.failed_attempts)
        else:
            log_attempt(None, False)
            flash('Usuario o contraseña incorrectos.')

    return render_template("index.html", form=user_form)

@app.route("/pagePrincipal")
def pagePrincipal():
    return render_template('layout.html')

#Función del Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')
common_passwords = ['123456', 'password', '12345678', 'qwerty', '123456789']

#Funcion que permite hacer el CRUD de los usuarios
@app.route("/pagePrincipal/user", methods=["GET", "POST"])
@login_required
@admin_required
def user():
    user_formreg = forms.UserFormReg(request.form)
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
                                usuario_registro=request.form.get('idUser'),
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
            
            
    return render_template('modules/usuarios.html', form=user_formreg,users=allUsuarios,alert=alert)

#Función del CRUD de Proveedores
@app.route("/pagePrincipal/proveedor", methods=["GET", "POST"])
@login_required
@admin_required
def proveedor():
    provee_formreg = forms.ProveedorFormReg(request.form)
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
    
    
    return render_template('modules/proveedores.html',form=provee_formreg,proveedores=allProveedores)


@app.route("/pagePrincipal/ventas", methods=["GET", "POST"])
@login_required
def ventas():
    #provee_formreg = forms.ProveedorFormReg(request.form)
    productos=VistaDetalleProducto.query.all()
    if request.method == 'POST':
        if request.form.get('registrar'):
            print('Hola') 
    
    return render_template('modules/ventaGalletasInd.html',productos=productos)


if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()