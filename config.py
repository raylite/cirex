import os, binascii
from dotenv import load_dotenv

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(APP_ROOT, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or binascii.hexlify(os.urandom(24))
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
    ALLOWED_EXTENSIONS = set(['txt', 'csv', 'ris'])
    SERVING_FILE = ''
    CITATIONS_RECORD = ''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://cirex_admin:p@55w0rd@localhost/cirex_db?charset=utf8mb4&binary_prefix=true'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MYSQL_DATABASE_CHARSET = 'utf8mb4'
    ##configs to handle error notification
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') 
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    ADMINS = ['qasimbabatunde@gmail.com']
