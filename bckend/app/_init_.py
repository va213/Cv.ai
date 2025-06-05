from flask import Flask
from flask_cors import CORS
from .routes.cv_routes import cv_bp

def create_app():
    app = Flask(__name__)

    CORS(app,origins="http://localhost:3000")

    app.register_blueprint(cv_bp)
    return app
