from flask import Flask
from flask_cors import CORS
from .routes.cv_routes import cv_bp
from .log_config import setup_logger

def create_app():
    logger = setup_logger()
    app = Flask(__name__)
    
    CORS(app,origins="http://localhost:3000")
    logger.info('app was started')


    app.register_blueprint(cv_bp)
    return app
