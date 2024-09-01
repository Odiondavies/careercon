from flask import Flask
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from ccapp import config


csrf = CSRFProtect()
mail = Mail()


def create_app():
    from ccapp.models import db
    myapp = Flask(__name__, instance_relative_config=True)
    myapp.config.from_pyfile('config.py', silent=True)
    myapp.config.from_object(config.DevelopmentConfig)
    db.init_app(myapp)
    csrf.init_app(myapp)
    migrate = Migrate(myapp, db)
    mail.init_app(myapp)
    return myapp


app = create_app()


from ccapp import forms, jobseeker_routes, employer_routes, routes

