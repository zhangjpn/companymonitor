# -*-coding:utf-8 -*-

from flask import Flask
from app.admin import admin_bp
from flask_cors import CORS

def create_app():

    app = Flask(__name__)
    app.config.from_object('app.config')

    app.register_blueprint(blueprint=admin_bp)
    CORS(app)  # 允许跨域访问
    return app
