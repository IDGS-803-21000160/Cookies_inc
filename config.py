import os
import urllib

class Config(object):
    SECRET_KEY = 'Clave_nueva'
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@127.0.0.1/cookiesInc'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
