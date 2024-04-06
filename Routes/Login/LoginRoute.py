from flask import  render_template, request, redirect, url_for, flash, current_app, Blueprint
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,login_user,logout_user,login_required,current_user



from Entities.Inventario import Usuario,LoginLog
from Entities.UsuarioForm import UsersForm
from Entities.Inventario import db
from Routes.Inventario.InventarioRoute import modulo_inventario
from Routes.Dashboard.DashboardRoutes import modulo_dashboard


modulo_login=Blueprint('modulo_login',__name__)



@modulo_login.route('/', methods=["GET", "POST"])
def index():
    user_form = UsersForm(request.form)
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
            user_id = user.id_usuario
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
                    return redirect(url_for('modulo_login.pagePrincipal'))
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

    return render_template("Login/login.html", form=user_form)

@modulo_login.route("/pagePrincipal")
def pagePrincipal():
    return redirect(url_for('modulo_dashboard.dashboard'))

@modulo_login.route('/logout')
def logout():
    logout_user()
    return redirect('/')