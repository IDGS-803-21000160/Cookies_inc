import os
import urllib

class Config(object):
    SECRET_KEY = 'Clave_nueva'
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root1234@127.0.0.1/cookiesInc'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    port = 5000
    SECRET_KEY = "miLlave"
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '1234'
    MYSQL_DB = 'cookiesInc'
    MYSQL_CURSORCLASS = 'DictCursor'
    MAX_FAILED_ATTEMPTS = 3
    TIME_TO_UNLOCK = 20
