import os
import urllib

class Config(object):
    SECRET_KEY = 'Clave_nueva'
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admincookies:Karelyruiz123@cookies.mysql.database.azure.com/cookiesInc'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
