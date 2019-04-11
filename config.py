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
        'sqlite:///' + os.path.join(APP_ROOT, 'cirex_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW'))
    MYSQL_DATABASE_CHARSET = 'utf8mb4'
    ##configs to handle error notification
    MAIL_SERVER = os.environ.get('MAIL_SERVER') 
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') 
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    ADMINS = ['qasimbabatunde@gmail.com']
