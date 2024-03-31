from flask import Flask, render_template, request, jsonify, flash, redirect, session,url_for
from flask_mysqldb import MySQL,MySQLdb #pip install flask-mysqldb https://github.com/alexferl/flask-mysqldb
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_cors import CORS, cross_origin
from functools import wraps
from flask_wtf.csrf import CSRFProtect
import forms
from datetime import datetime

from config import DevelopmentConfig

 
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()
#BLOQUEAR TODOS LOS ORIGENES
#CORS(app, resources={r"/*": {"origins": ""}})

#DESBLOQUEAR TODOS LOS ORIGENES
#CORS(app, resources={r"/*": {"origins": "*"}})

# DESBLOQUEAR CIERTOS ORIGENES
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5000"]}})
#CORS(app, resources={r"/*": {"origins": ["http://192.168.111.246.*", "http://192.168.111.86:8080","http://192.168.111.127.*"]}})

mysql = MySQL(app)

#--------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.route('/',methods=["GET","POST"])
def index():
    username=''
    password=''
    msg=''
    cur=''
    user_form = forms.UsersForm(request.form)

    if request.method == 'POST' and user_form.validate():
        username = user_form.username.data
        password = user_form.password.data
        # print(generate_password_hash('V1ct0rG@y', "scrypt", 16))

        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM GetAllUsuarios WHERE admin_name = %s", [username])
            user_data = cur.fetchone()
            

            if user_data:
                if user_data['account_locked']:
                    # Verifica si ha pasado el tiempo de bloqueo
                    lock_time = user_data['lock_time']
                    if lock_time is not None and (datetime.now() - lock_time).total_seconds() < DevelopmentConfig.TIME_TO_UNLOCK:
                        # Si la cuenta está bloqueada pero el tiempo de bloqueo no ha pasado, muestra un mensaje de cuenta bloqueada temporalmente
                        msg = 'Your account is temporarily locked. Please try again later.'
                        print('segundos transcurridos', (datetime.now() - lock_time).total_seconds())
                        print(msg)
                        return render_template("index.html", form=user_form, msg=msg)
                    else:
                         # Si ha pasado el tiempo de bloqueo, desbloquea la cuenta usando el procedimiento almacenado
                        cur.callproc('ToggleUserLock', (username, False))
                        mysql.connection.commit()
                db_password = user_data['admin_password']
                failed_attempts = user_data['failed_login_attempt']

                if failed_attempts >= DevelopmentConfig.MAX_FAILED_ATTEMPTS:
                    # Bloquea la cuenta si ha excedido el número máximo de intentos fallidos
                    cur.callproc('ToggleUserLock', (username, True))
                    mysql.connection.commit()
                    msg = 'Too many failed login attempts. Please try again later.'
                elif check_password_hash(db_password, password):
                    session['logged_in'] = True
                    session['username'] = username
                    # Llamar al procedimiento almacenado para actualizar los intentos fallidos
                    cur.execute("CALL UpdateFailedLoginAttempts(%s, %s)", (username, 0))
                    mysql.connection.commit()
                    # Registro de log de inicio de sesión exitoso
                    log_login_attempt(username, True, None)
                    msg="success"
                    return redirect('principal')
                else:
                    msg = 'Invalid credentials'
                    # Incrementar el contador de intentos fallidos
                    cur.execute("CALL UpdateFailedLoginAttempts(%s, %s)", (username, failed_attempts + 1))
                    mysql.connection.commit()
                    log_login_attempt(username, False, msg)
            else:
                msg = 'User not found'
                log_login_attempt(username, False, msg)

        except Exception as e:
            # Manejar errores de base de datos de manera adecuada
            #msg = 'Error occurred: {}'.format(str(e))
            msg = 'Usuario sin intentos por la siguiente hora, intente mas tarde.'
            # Registro de log de inicio de sesión fallido
            log_login_attempt(username, False, str(e))
        finally:
            # Cerrar el cursor después de haber trabajado con los datos
            if cur:
                cur.close()
        return render_template("index.html",form=user_form, msg=msg)
    return render_template("index.html",form=user_form)

@app.route('/action2', methods=["POST"])
def action2():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "POST":
        data = request.get_json()  # Get JSON data from the request
        if 'username' in data and 'password' in data:
            username = data['username']
            password = data['password']

            try:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("SELECT * FROM usuario WHERE admin_name = %s", [username])
                user_data = cur.fetchone()
                cur.close()

                if user_data:
                    db_password = user_data['admin_password']
                    if check_password_hash(db_password, password):
                        session['logged_in'] = True
                        session['username'] = username
                        msg = 'success'
                    else:
                        msg = 'Invalid credentials'
                else:
                    msg = 'User not found'

            except Exception as e:
                # Manejar errores de base de datos de manera adecuada
                msg = 'Error occurred: {}'.format(str(e))
        else:
            msg = 'Missing username or password in the request'

    else:
        msg = 'Invalid request method'

    return jsonify({'msg': msg})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/principal')
@login_required
def principal():        
    #Agregar mensajes a la lista de flash
    mensaje='Bienvenido a la app'
    flash(mensaje)
    return render_template('principal.html')



def log_login_attempt(username, success, error_message):
    try:
        cur = mysql.connection.cursor()
        # Llamada al procedimiento almacenado en lugar de la consulta directa
        cur.callproc('InsertarLoginLog', (username, success, error_message))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print("Error occurred while logging login attempt:", str(e))

if __name__ == "__main__":
    csrf.init_app(app)
    app.run(port=DevelopmentConfig.port, host='0.0.0.0')