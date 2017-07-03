# -*-coding:utf-8 -*-
from flask import Blueprint

admin_bp = Blueprint('admin_bp', import_name=__name__)

from . import views
