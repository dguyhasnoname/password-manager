"""Flask config."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """Set Flask config variables."""

    FLASK_ENV = 'development' # enables debug
    #SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    # Database
    MONGO_URI = environ.get('MONGO_URI')
    MONGO_USER = environ.get('MONGO_USER')
    MONGO_PASSWORD = environ.get('MONGO_PASSWORD')    

    #password encode key
    PASSWORD_MANAGER_KEY = environ.get('PASSWORD_MANAGER_KEY')