#coding:utf8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:x5@localhost:3306/micromovie"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS	"] = True

db = SQLAlchemy(app)

#会员模型
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer,primary_key = True)#编号
    name = db.Column(db.String(100),unique=True)#昵称
    pwd = db.Column(db.String(100))#密码
    email = db.Column(db.String(100),unique=True)#邮箱
    phone = db.Column(db.String(11),unique=True)#手机号
    info = db.Column(db.Text)#个人信息
    face = db.Column(db.String(255),unique=True)#头像
    addtime = db.Column(db.DateTime,index = True,default=datetime.utcnow)#申请时间
    uuid = db.Column(db.String(255),unique=True)# uuid
    userlogs = db.relationship('Userlog', backref='user')#会员日志登录日志关联

    def __repr__(self):
        return '<User %r>' % self.name

#会员登录日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer,primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip = db.Column(db.String(100))# ip
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  #加入时间

    def __repr__(self):
        return '<Userlog %r>' % self.id

#标签
class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer,primary_key = True)#编号
    name = db.Column(db.String(100),unique=True)#标题
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)  #加入时间
    movies = db.relationship('Movie', backref='tag') #电影外键关系关联

    def __repr__(self):
        return '<Tag %r>' % self.name

#电影
class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer,primary_key = True)#编号
    title = db.Column(db.String(255),unique=True)#标题
    url = db.Column(db.String(255),unique=True)#电影地址
    info = db.Column(db.Text)#个人信息
    logo = db.Column(db.String(255),unique=True)#电影logo
    star = db.Column(db.SmallInteger)
    playnum = db.Column(db.BigInteger)
    commentnum = db.Column(db.BigInteger)
    tag_id = db.Column(db.Integer,db.ForeignKey('tag.id'))
    area = db.Column(db.String(255))#电影logo
    release_time = db.Column(db.Date)
    lenght = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<movie %r>' % self.title

#上映预告
class Preview(db.Model):
    __tablename__ = "preview"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 标题
    logo = db.Column(db.String(255), unique=True)  # 电影logo
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)