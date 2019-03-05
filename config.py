import os, binascii

APP_ROOT = os.path.abspath(os.path.dirname(__file__))

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
