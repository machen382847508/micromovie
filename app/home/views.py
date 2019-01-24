# coding:utf8
from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegistForm, LoginForm, UserdetailForm, PwdForm, CommentForm
from app.models import User, Comment, Movie, Userlog, Preview, Tag, Moviecol
from app.home.utils import Utils
from app import db, app
from functools import wraps
import uuid, os, json
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from datetime import datetime

util = Utils()


# 验证是否在登录状态
def admin_login_req(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("user.login", next=request.url))
        return func(*args, **kwargs)

    return wrapper


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


@home.route("/<int:page>/", methods=["GET"])
def index(page):
    tags = Tag.query.all()
    page_data = Movie.query
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm
    )
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=10)
    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


@home.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter(
            or_(User.name == data["account"], User.email == data["account"], User.phone == data["account"])).first()
        if user.pwd == data["pwd"]:
            session["user"] = user.name
            session["user_id"] = user.id
            util.InsertUserlog()
            return redirect(url_for("home.user"))
        else:
            flash("登录失败", "err")
            return render_template("home/login.html", form=form)
    return render_template("home/login.html", form=form)


@home.route("/logout/")
@admin_login_req
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("home.login"))


# 会员注册功能
@home.route("/regist/", methods=['GET', 'POST'])
@admin_login_req
def regist():
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            pwd=data["pwd"],
            phone=data["phone"],
            email=data["email"],
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功", "ok")
        return redirect(url_for("home.login"))
    return render_template("home/regist.html", form=form)


@home.route("/user/", methods=['GET', 'POST'])
@admin_login_req
def user():
    form = UserdetailForm()
    user = User.query.get(int(session["user_id"]))
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        file_face = secure_filename(form.face.data.filename)
        if not os.path.exists(app.config["FC_DIR"]):
            os.makedirs(app.config["FC_DIR"])
            os.chmod(app.config["FC_DIR"], "rw")
        user.face = change_filename(file_face)
        form.face.data.save(app.config["FC_DIR"] + user.face)
        user.name = data["name"]
        user.email = data["email"]
        user.info = data["info"]
        user.phone = data["phone"]
        db.session.add(user)
        db.session.commit()
        flash("会员信息修改成功", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


@home.route("/pwd/", methods=['GET', 'POST'])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.get(int(session["user_id"]))
        if user.pwd != data["oldpwd"]:
            flash("旧密码输入错误", "err")
            return redirect(url_for("home.pwd"))
        elif data["oldpwd"] == data["newpwd"]:
            flash("旧密码和新密码相同，无需修改", "err")
            return redirect(url_for("home.pwd"))
        user.pwd = data["newpwd"]
        db.session.add(user)
        db.session.commit()
        flash("密码修改成功", "ok")
        return redirect(url_for("home.pwd"))
    return render_template("home/pwd.html", form=form)


@home.route("/comments/<int:page>/", methods=['GET', 'POST'])
@admin_login_req
def comments(page=None):
    if page is None:
        page = 1

    page_data = Comment.query.join(Movie).join(User).filter(
        Comment.movie_id == Movie.id, Comment.user_id == User.id) \
        .order_by(Comment.addtime.desc()).paginate(page=page, per_page=10)

    return render_template("home/comments.html", page_data=page_data)


@home.route("/loginlog/<int:page>/", methods=['GET', 'POST'])
def loginlog(page):
    if page is None:
        page = 1
    page_data = Userlog.query.join(User).filter(User.id == Userlog.user_id).order_by(Userlog.addtime.desc()).paginate(
        page=page, per_page=10)

    return render_template("home/loginlog.html", page_data=page_data)


@home.route("/moviecol/add/", methods=['GET'])
def moviecol_add():
    uid = request.args.get("uid", "")
    mid = request.args.get("mid", "")
    moviecol = Moviecol.query.filter_by(
        user_id=int(uid),
        movie_id=int(mid)
    ).count()
    if moviecol == 1:
        data = dict(ok=0)
    elif moviecol == 0:
        moviecol = Moviecol(
            user_id=int(uid),
            movie_id=int(mid)
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)
    return json.dumps(data)


@home.route("/moviecol/<int:page>/", methods=['GET'])
def moviecol(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(
        page=page, per_page=10)
    return render_template("home/moviecol.html", page_data=page_data)


# 动态
@home.route("/amination/")
def amination():
    data = Preview.query.all()
    return render_template("home/amination.html", data=data)


# 搜索界面
@home.route("/search/<int:page>/")
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    movie_count = Movie.query.filter(Movie.title.ilike('%' + key + '%')).count()
    page_data = Movie.query.filter(Movie.title.ilike('%' + key + '%')).order_by(Movie.addtime.desc()).paginate(
        page=page, per_page=10)
    return render_template("home/search.html", key=key, page_data=page_data, movie_count=movie_count)


# 详情
@home.route("/play/<int:id>/<int:page>", methods=['GET', 'POST'])
def play(id=None, page=None):
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1

    page_data = Comment.query.join(Movie).join(User).filter(
        movie.id == Movie.id, session["user_id"] == User.id) \
        .order_by(Comment.addtime.desc()).paginate(page=page, per_page=10)

    comment_num = Comment.query.join(Movie).join(User).filter(
        movie.id == Movie.id, session["user_id"] == User.id).count()

    movie.playnum = movie.playnum + 1
    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功", "ok")
        return redirect(url_for('home.play', id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html", movie=movie, form=form, page_data=page_data, comment_num=comment_num)
