import os
import urllib

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Clave_nueva')
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    DEBUG = True
    DB_USER = os.environ.get('DB_USER', 'adminCookiesIc')
    DB_PASS = os.environ.get('DB_PASS', 'g@llet@sCook2024')
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_NAME = os.environ.get('DB_NAME', 'cookiesIncF')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{urllib.parse.quote_plus(DB_PASS)}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
