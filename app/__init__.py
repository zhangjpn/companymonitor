# -*-coding:utf-8 -*-

from flask import Flask
from app.admin import admin_bp


def create_app():

    app = Flask(__name__)
    app.config.from_object('app.config')

    app.register_blueprint(blueprint=admin_bp)

    return app
