#coding:utf8
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:x5@localhost:3306/micromovie"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SECRET_KEY"]='8ac6eb5d94a449dca18f0501eef3e591'
app.config["UP_DIR"] = os.path.join(os.path.dirname(__file__),"static/upload/")
app.config["FC_DIR"] = os.path.join(os.path.dirname(__file__),"static/upload/user/")
app.debug = True
db = SQLAlchemy(app)
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint,url_prefix="/home")
app.register_blueprint(admin_blueprint,url_prefix="/admin")

#错误地址捕获
@app.errorhandler(404)
def page_not_find(error):
    return render_template('home/404.html'),404
