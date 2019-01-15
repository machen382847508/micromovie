# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError
from app.models import Admin, Movie,Tag,Preview


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

