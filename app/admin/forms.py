# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField,SelectMultipleField
from wtforms.validators import DataRequired, ValidationError,EqualTo
from app.models import Admin, Tag,Auth,Role

auths = Auth.query.all()

class LoginForm(FlaskForm):
    '''管理员登录表单'''
    account = StringField(
        label="账号:",
        validators=[
            DataRequired("请输入账号")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
        }
    )

    pwd = PasswordField(
        label="密码:",
        validators=[
            DataRequired("请输入密码")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
        }
    )

    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )

    # 账号验证
    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在！")


# 标签表单
class TagForm(FlaskForm):
    name = StringField(
        label="标签名称",
        validators=[
            DataRequired("请输入标签名称")
        ],
        description="标签",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入标签名称！"
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary"
        }
    )


# 电影表单
class MovieForm(FlaskForm):
    title = StringField(
        label="片名",
        validators=[
            DataRequired("请输入片名")
        ],
        description="片名",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片名！"
        }
    )

    url = FileField(
        label="文件",
        validators=[
            DataRequired("请上传文件")
        ],
        description="文件",
        render_kw={
            "id": "input_url"
        }
    )

    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入片名")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": "10"
        }
    )

    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面")
        ],
        description="封面"
    )

    star = SelectField(
        label="星级",
        validators=[DataRequired("请选择星级！")],
        description="星级",
        coerce=int,
        choices=[(1,"1星"),(2,"2星"),(3,"3星"),(4,"4星"),(5,"5星")],
        render_kw = { "class": "form-control" }
    )

    tag_id = SelectField(
        label="标签",
        validators=[DataRequired("请选择标签！")],
        coerce=int,
        choices = [(v.id,v.name) for v in Tag.query.all()],
        render_kw={
            "class": "form-control"
        }
    )

    area = StringField(
        label="地区",
        validators=[
            DataRequired("请输入地区")
        ],
        description="地区",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入地区！"
        }
    )

    length = StringField(
        label="片长",
        validators=[
            DataRequired("请输入片长")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入地区！"
        }
    )

    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("请输入上映时间")
        ],
        description="上映时间",
        render_kw={
            "class": "form-control",
            "placeholder": "请选择上映时间！",
            "id": "input_release_time"
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary"
        }
    )

class PreviewForm(FlaskForm):
    title = StringField(
        label="预告标题",
        validators=[
            DataRequired("请输入预告标题")
        ],
        description="预告标题",
        render_kw={
            "class":"form-control" ,
            "id":"input_title" ,
            "placeholder":"请输入预告标题！"
        }
    )

    logo = FileField(
        label="预告封面",
        validators=[
            DataRequired("请上传预告封面")
        ],
        description="预告封面",
        render_kw={
            "id":"input_logo"
        }
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )

class UserForm(FlaskForm):

    id = StringField(
        label="编号",
        description="编号"
    )

    name = StringField(
        label="昵称",
        description="昵称"
    )

    email = StringField(
        label="邮箱",
        description="邮箱"
    )

    phone = StringField(
        label="电话",
        description="电话"
    )

    face = TextAreaField(
        label="头像",
        description="头像"
    )

    addtime = StringField(
        label="注册时间",
        description="注册时间"
    )

    uuid = StringField(
        label="唯一标志符",
        description="唯一标志符"
    )

    info = StringField(
        label="个性简介",
        description="个性简介"
    )

class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码:",
        validators=[
            DataRequired("请输入旧密码")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！"
        }
    )

    new_pwd = PasswordField(
        label="新密码:",
        validators=[
            DataRequired("请输入新密码")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！"
        }
    )

    new_pwd_again = PasswordField(
        label="确认新密码:",
        validators=[
            DataRequired("请输入确定新密码")
        ],
        description="确认确定新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入确定新密码！"
        }
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )

    # 密码验证
    def validate_old_pwd(self, field):
        from flask import session
        pwd = field.data
        name = session["admin"]
        admin = Admin.query.filter_by(
            name = name
        ).first()
        if not admin.check_pwd(pwd):
            raise ValidationError("旧密码不存在！")

class AuthForm(FlaskForm):
    name = StringField(
        label="权限名称",
        validators=[
            DataRequired("请输入权限名称")
        ],
        description="标签",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限名称！"
        }
    )

    url = StringField(
        label="权限地址",
        validators=[
            DataRequired("请输入权限地址")
        ],
        description="标签",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限地址！"
        }
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )

class RoleForm(FlaskForm):
    name = StringField(
        label="角色名称",
        validators=[
            DataRequired("请输入角色名称")
        ],
        description="角色名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入角色名称！"
        }
    )

    auths = SelectMultipleField(
        label = "权限列表",
        validators=[
            DataRequired("请选择权限列表")
        ],
        coerce=int,
        choices=[(v.id,v.name) for v in Auth.query.all()],
        description="权限列表",
        render_kw={
            "class": "form-control"
        }
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )

class AdminForm(FlaskForm):
    name = StringField(
        label="管理员名称",
        validators=[
            DataRequired("请输入管理员名称")
        ],
        description="管理员名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员名称！"
        }
    )

    pwd = PasswordField(
        label="管理员密码:",
        validators=[
            DataRequired("请输入管理员密码")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码！"
        }
    )

    new_pwd = PasswordField(
        label="管理员重复密码:",
        validators=[
            DataRequired("请输入管理员重复密码"),
            EqualTo('pwd', message="两次密码输入不一致！")
        ],
        description="管理员重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员重复密码！"
        }
    )

    role_id = SelectField(
        label = "所属角色",
        validators=[
            DataRequired("请选择所属角色列表")
        ],
        coerce=int,
        choices=[(v.id,v.name) for v in Role.query.all()],
        description="所属角色",
        render_kw={
            "class": "form-control"
        }
    )

    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )

    def validate_name(self, field):
        auth = Admin.query.filter_by(name=field.data).count()
        if auth == 1:
            raise ValidationError("管理员名称已经存在！")
