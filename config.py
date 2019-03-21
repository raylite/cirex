import os, binascii
from dotenv import load_dotenv

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(APP_ROOT, '.env'))

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or binascii.hexlify(os.urandom(24))
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
    ALLOWED_EXTENSIONS = set(['txt', 'csv', 'ris'])
    SERVING_FILE = ''
    CITATIONS_RECORD = ''
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'mysql://cirex_admin:p@55w0rd@localhost/cirex_db?charset=utf8mb4&binary_prefix=true'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MYSQL_DATABASE_CHARSET = 'utf8mb4'
    ##configs to handle error notification
    MAIL_SERVER = os.getenv('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') 
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') 
    ADMINS = ['qasimbabatunde@gmail.com']
