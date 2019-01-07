#coding:utf8
#引入蓝图文件
from flask import Blueprint

admin = Blueprint("admin",__name__)

import app.admin.views