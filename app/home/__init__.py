#coding:utf8
#引入蓝图文件
from flask import Blueprint

home = Blueprint("home",__name__)

import app.home.views