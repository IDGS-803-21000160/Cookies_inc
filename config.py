import os
import urllib
from cryptography.fernet import Fernet


cipher_suite = Fernet(b'Vy_FbseWXQ-ry5W4KkK6QiQL4Jnu_5qO-DpuNgZAjJg=')

encrypted_DB_USER =b'gAAAAABmFzIPbORiRrtZC4_Nf-6PphEUIBA1rRHh_v9XaV0xz9psrRv9uNNtoKZVT0xfQx9g7bZTre5Dnubu6ZeD1mnZRrae_w=='
encrypted_DB_PASS =b'gAAAAABmFzIPk1lo3WwqnVpYchEnMiSz_cT6aeQAs-z9hzlDvZAVSl36YdXlQ0P4PBHVvxokSZVaNVEfOAxh0LwugageCqjkYfAftjLdNr2Vi8IPzR6hepQ='
encrypted_DB_HOST =b'gAAAAABmFzIPVpalnJhea6WDr8DNVSMh59tKoRBLUU2M1L3aEbgz9yijemdKB66684-D8h-l4nXkWXp3Oh62FIUw39WFLgU1jg=='
encrypted_DB_NAME =b'gAAAAABmFzIPbV7yEcRN4WxpXuecJWJo0Ou44rzcsJC5A08R9XTm2EKjFuAOVU1SWtC1UZRKas4Eb7QV1xBRhjt1ZMyuHpVYeA=='


decrypted_DB_USER = cipher_suite.decrypt(encrypted_DB_USER).decode()
decrypted_DB_PASS = cipher_suite.decrypt(encrypted_DB_PASS).decode()
decrypted_DB_HOST = cipher_suite.decrypt(encrypted_DB_HOST).decode()
decrypted_DB_NAME = cipher_suite.decrypt(encrypted_DB_NAME).decode()
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Clave_nueva')
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):

    # print(decrypted_DB_USER)
    # print(decrypted_DB_PASS)
    # print(decrypted_DB_HOST)
    # print(decrypted_DB_NAME)

    DEBUG = True
    DB_USER = os.environ.get('DB_USER', decrypted_DB_USER)
    DB_PASS = os.environ.get('DB_PASS', decrypted_DB_PASS)
    DB_HOST = os.environ.get('DB_HOST', decrypted_DB_HOST)
    DB_NAME = os.environ.get('DB_NAME', decrypted_DB_NAME)
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{urllib.parse.quote_plus(DB_PASS)}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

