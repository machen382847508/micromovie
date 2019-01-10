#coding:utf8

from datetime import datetime
from app import db

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
    addtime = db.Column(db.DateTime,index = True,default=datetime.now())#申请时间
    uuid = db.Column(db.String(255),unique=True)# uuid
    userlogs = db.relationship('Userlog', backref='user')#会员日志登录日志关联
    comments = db.relationship('Comment', backref='user')#关联评论
    moviecols = db.relationship('Moviecol', backref='user')  # 关联评论

    def __repr__(self):
        return '<User %r>' % self.name

#会员登录日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer,primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip = db.Column(db.String(100))# ip
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  #加入时间

    def __repr__(self):
        return '<Userlog %r>' % self.id

#标签
class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer,primary_key = True)#编号
    name = db.Column(db.String(100),unique=True)#标题
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  #加入时间
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
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    comments = db.relationship('Comment', backref='movie')  # 电影关联表
    moviecols = db.relationship('Moviecol', backref='movie')  # 关联评论

    def __repr__(self):
        return '<movie %r>' % self.title

#上映预告
class Preview(db.Model):
    __tablename__ = "preview"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 标题
    logo = db.Column(db.String(255), unique=True)  # 电影logo
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)


#评论
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)  # 标题
    movie_id = db.Column(db.Integer,db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Comment %r>' % self.id

#电影收藏
class Moviecol(db.Model):
    __tablename__ = "moviecol"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)  # 标题
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Moviecol %r>' % self.id

# 权限
class Auth(db.Model):
    __tablename__ = "auth"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(255), unique=True)  # 权限名称
    url = db.Column(db.String(255), unique=True)  # 路由地址
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Auth %r>' % self.name

#角色
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 角色名称
    auths = db.Column(db.String(600))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<Role %r>' % self.name

#管理员模块
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)  # 管理员编号
    name = db.Column(db.String(100), unique=True)  # 管理员昵称
    pwd = db.Column(db.String(100))  # 管理员密码
    is_super = db.Column(db.SmallInteger) #是否是超级管理
    role_id  = db.Column(db.Integer, db.ForeignKey('role.id'))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    adminlogs = db.relationship('Adminlog', backref='admin')  # 关联评论
    oplogs = db.relationship('Oplog', backref='admin')  # 操作关联

    def __repr__(self):
        return '<Admin %r>' % self.name

    def check_pwd(self, pwd):
        # from werkzeug.security import check_password_hash
        # return check_password_hash(self.pwd, pwd)  # 验证密码是否正确，返回True和False
        if (self.pwd == pwd):
            return True
        else:
            return False

#管理员登录日志
class Adminlog(db.Model):
    __tablename__ = "adminlog"
    id = db.Column(db.Integer,primary_key = True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    ip = db.Column(db.String(100))# ip
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  #加入时间

    def __repr__(self):
        return '<Userlog %r>' % self.id

#操作日志
class Oplog(db.Model):
    __tablename__ = "oplog"
    id = db.Column(db.Integer,primary_key = True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    ip = db.Column(db.String(100))# ip
    reason = db.Column(db.String(600))#操作原因
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  #加入时间

    def __repr__(self):
        return '<Oplog %r>' % self.id

