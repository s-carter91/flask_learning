from flask import Flask
from init import db, ma, bcrypt, jwt
from controllers.cards_controller import cards_bp
from controllers.auth_controller import auth_bp
import os

def create_app():
    app = Flask(__name__)

    @app.errorhandler(404)
    def not_found(err):
        print(err)
        return {'error' : str(err)}, 404

    
    app.config ['JSON_SORT_KEYS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(cards_bp)
    app.register_blueprint(auth_bp)

    return app
