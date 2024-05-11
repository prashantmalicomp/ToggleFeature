import os
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from dotenv import load_dotenv
from app.toggles.views import toggle_blueprint
from app.users.views import users_blueprint
from app.models import db


# Load environment variables from .env file
load_dotenv()


migrate = Migrate()
ma = Marshmallow()

def create_app(env="development"):
    
    app = Flask(__name__)
    env = env if not os.environ.get('FLASK_ENV') else os.environ.get('FLASK_ENV')

    # Database Configuration based on environment
    if env == 'development':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    elif env == 'qa':
        SQLALCHEMY_DATABASE_URI = os.environ.get('QA_DATABASE_URI')
    elif env == 'production':
        SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URI')
    elif env == 'testing':
        SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URI')
    else:
        raise ValueError("Invalid environment specified")

    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

    app.config['SECRET_KEY'] = 'dev'

    app.config['DEBUG'] = True

    # app.config['FLASK_DEBUG'] = True

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # Register the Blueprint with the Flask app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(toggle_blueprint)
    # app.register_blueprint(api_v1)

    return app