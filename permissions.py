from flask import Flask,render_template,flash,redirect,url_for
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from functools import wraps
from Routes.Dashboard.DashboardRoutes import modulo_dashboard



def pos_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and (current_user.tipousuario == 'opPOS' or current_user.tipousuario == 'Administrador' ):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('modulo_dashboard.dashboard'))
    return decorated_function

def inventario_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and (current_user.tipousuario == 'adminInventario' or current_user.tipousuario == 'Administrador' ):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('modulo_dashboard.dashboard'))
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and  current_user.tipousuario == 'Administrador':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('modulo_dashboard.dashboard'))
    return decorated_function