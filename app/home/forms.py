# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, SubmitField, FileField, TextAreaField, SelectField,SelectMultipleField
from wtforms.validators import DataRequired, ValidationError,EqualTo ,Email,Regexp
from app.models import User
from sqlalchemy import or_

class RegistForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称")
        ],
        description="昵称",
        render_kw={
            "class":"form-control input-lg",
            "placeholder":"昵称"
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱"),
            Email("请输入正确的邮箱格式")
        ],
        description="昵称",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "邮箱"
        }
    )

    phone = StringField(
        label="电话",
        validators=[
            DataRequired("请输入电话"),
            Regexp(r"^1[35678]\d{9}$",message="手机格式输入不正确")
        ],
        description="电话",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "电话",
            "maxlength":11
        }
    )

    pwd = PasswordField(
        label="密码:",
        validators=[
            DataRequired("请输入密码")
        ],
        description="密码",
        render_kw={
            "class": "form-control  input-lg",
            "placeholder": "请输入密码！",
        }
    )

    repwd = PasswordField(
        label="确认密码:",
        validators=[
            DataRequired("请输入确认密码"),
            EqualTo('pwd', message="两次密码输入不一致！")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入确认密码！",
        }
    )

    submit = SubmitField(
        label="注册",
        render_kw={
            "class":"btn btn-lg btn-success btn-block"
        }
    )

    def validate_name(self,field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 1:
            raise ValidationError("用户名已经存在！")

    def validate_email(self,field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError("用户邮箱已经存在！")

    def validate_phone(self,field):
        phone = field.data
        user = User.query.filter_by(phone=phone).count()
        if user == 1:
            raise ValidationError("用户电话已经存在！")

class LoginForm(FlaskForm):
    account = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号")
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "用户名/邮箱/手机号码！"
        }
    )

    pwd = PasswordField(
        label="密码:",
        validators=[
            DataRequired("请输入密码")
        ],
        description="密码",
        render_kw={
            "class": "form-control  input-lg",
            "placeholder": "请输入密码！",
        }
    )

    submit = SubmitField(
        label="登录",
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    def validate_account(self,field):
        account = field.data
        user = User.query.filter(or_(User.name == account, User.email == account, User.phone == account)).count()
        if user == 0:
            raise ValidationError("账户不存在！")

class UserdetailForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "昵称"
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱"),
            Email("请输入正确的邮箱格式")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "邮箱"
        }
    )

    phone = StringField(
        label="电话",
        validators=[
            DataRequired("请输入电话"),
            Regexp(r"^1[35678]\d{9}$", message="手机格式输入不正确")
        ],
        description="电话",
        render_kw={
            "class": "form-control",
            "placeholder": "电话",
            "maxlength": 11
        }
    )

    face = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像")
        ],
        description="头像"
    )

    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class":"form-control",
            "rows":10
        }
    )

    submit = SubmitField(
        label="保存修改",
        render_kw={
            "class": "btn btn-success"
        }
    )

class PwdForm(FlaskForm):
    oldpwd = PasswordField(
        label="旧密码:",
        validators=[
            DataRequired("请输入旧密码")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
        }
    )

    newpwd = PasswordField(
        label="新密码:",
        validators=[
            DataRequired("请输入新密码")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
        }
    )

    submit = SubmitField(
        label="修改密码",
        render_kw={
            "class": "btn btn-success"
        }
    )

class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("请输入内容！")
        ],
        description="内容",
        render_kw={
            "class": "form-control",
            "rows": 10
        }
    )

    submit = SubmitField(
        label="提交评论",
        render_kw={
            "class":"btn btn-success" ,
            "id":"btn-sub"
        }
    )