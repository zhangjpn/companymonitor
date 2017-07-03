# -*-coding:utf-8 -*-

from flask import Flask
from app.admin import admin_bp
from flask_cors import CORS
import redis


def create_app():

    app = Flask(__name__)
    app.config.from_object('app.config')
    app.redis = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'],
                            db=app.config['REDIS_DB'], password=app.config['REDIS_PASSWORD'])
    app.secret_key = app.config['SECRET_KEY']

    app.register_blueprint(blueprint=admin_bp)

    CORS(app)  # 允许跨域访问
    return app
