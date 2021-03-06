# coding:utf8
from . import admin,utils
from flask import render_template, redirect, url_for, flash, session, request,abort
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, UserForm,PwdForm,AuthForm,RoleForm,AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment,Moviecol,Oplog,Adminlog,Userlog,Auth,Role
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import os, datetime, uuid

util = utils.Utils()

@app.context_processor
def tpl_extra():
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data

#路由规则权限
def admin_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        admin = Admin.query.join(
            Role
        ).filter(Role.id == Admin.role_id, Admin.id == session["admin_id"]).first()
        auths = admin.role.auths
        auths = list(map(lambda v:int(v) , auths.split(",")))
        auth_list = Auth.query.all()
        urls = [v.url for v in auth_list for val in auths if val == v.id]
        rule = request.url_rule
        if str(rule) not in urls:
            abort(404)
        return func(*args, **kwargs)
    return wrapper

# 验证是否在登录状态
def admin_login_req(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return func(*args, **kwargs)

    return wrapper


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + "." + fileinfo[0]
    return filename


@admin.route("/")
@admin_login_req
def index():
    return render_template("admin/index.html")


@admin.route("/login/", methods=['GET', 'POST'])
@admin_login_req
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误","err")
            return redirect(url_for("admin.login"))
        else:
            session["admin"] = data["account"]
            session["admin_id"] = admin.id
            util.InsertAdminlog()
            return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return render_template("admin/login.html")


@admin.route("/pwd/", methods=['GET', 'POST'])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        if data["old_pwd"] == data["new_pwd"]:
            flash("新密码与旧密码相同，无需修改","err")
            return redirect(url_for("admin.pwd"))
        elif data["new_pwd"] != data["new_pwd_again"]:
            flash("新密码不等于旧密码", "err")
            return redirect(url_for("admin.pwd"))

        admin = Admin.query.filter_by(name = session["admin"]).first()
        admin.pwd = data["new_pwd"]
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功,请重新登录","ok")
        return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html",form = form)


@admin.route("/tag/add/", methods=['GET', 'POST'])
@admin_login_req
def tag_add():
    tagForm = TagForm()
    if tagForm.validate_on_submit():
        data = tagForm.data
        tag = Tag.query.filter_by(name=data["name"]).count()
        if tag == 1:
            flash("标签名称已经存在", "err")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(
            name=data["name"]
        )
        db.session.add(tag)
        db.session.commit()

        util.InsertOplog("添加电影标签:"+data["name"])
        flash("标签添加成功", "ok")
        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=tagForm)


# 标签列表分页
@admin.route("/tag/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def tag_list(page):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/tag_list.html", page_data=page_data)


# 删除标签
@admin.route("/tag/del/<int:id>/", methods=['GET'])
@admin_login_req
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签删除成功", "ok")
    util.InsertOplog("删除电影标签:" + tag.name)
    return redirect(url_for('admin.tag_list', page=1))


# 修改标签
@admin.route("/tag/edit/<int:id>/", methods=['GET', 'POST'])
@admin_login_req
def tag_edit(id):
    tagform = TagForm()
    tag = Tag.query.get_or_404(id)
    if tagform.validate_on_submit():
        data = tagform.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        if tag_count == 1 and tag.name != data["name"]:
            flash("名称已经存在", "err")
            return redirect(url_for("admin.tag_edit", id=id))
        tag.name = data["name"]
        db.session.add(tag)
        db.session.commit()
        flash("标签修改成功", "ok")
        util.InsertOplog("修改电影标签:" + tag.name)
        return redirect(url_for("admin.tag_list", page=1))
    return render_template("admin/tag_edit.html", form=tagform, tag=tag)


@admin.route("/movie/add/", methods=['GET', 'POST'])
@admin_login_req
def movie_add():
    movieform = MovieForm()
    if movieform.validate_on_submit():
        movieform.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]
        data = movieform.data
        file_url = secure_filename(movieform.url.data.filename)
        file_logo = secure_filename(movieform.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        movieform.url.data.save(app.config["UP_DIR"] + url)
        movieform.logo.data.save(app.config["UP_DIR"] + logo)
        movie = Movie(
            title=data["title"],
            url=url,
            info=data["info"],
            logo=logo,
            star=int(data["star"]),
            playnum=0,
            commentnum=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            lenght=data["length"]
        )
        db.session.add(movie)
        db.session.commit()
        flash("电影添加成功", "ok")
        util.InsertOplog("添加电影成功:" + movie.title)
        return redirect(url_for("admin.movie_add"))
    return render_template("admin/movie_add.html", form=movieform)


# 电影列表
@admin.route("/movie/list/<int:page>/", methods=['GET','POST'])
@admin_login_req
def movie_list(page):
    if page is None:
        page = 1
    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)


# 删除电影
@admin.route("/movie/del/<int:id>", methods=['GET'])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.filter_by(id=id).first_or_404()
    fileurl = app.config["UP_DIR"] + movie.url
    filelogo = app.config["UP_DIR"] + movie.logo
    if os.path.exists(fileurl) and os.path.exists(filelogo):
        os.remove(fileurl)
        os.remove(filelogo)

    db.session.delete(movie)
    db.session.commit()
    flash("电影删除成功", "ok")
    util.InsertOplog("删除电影成功:" + movie.title)
    return redirect(url_for('admin.movie_list', page=1))


# 编辑电影
@admin.route("/movie/edit/<int:id>/", methods=['GET', 'POST'])
@admin_login_req
def movie_edit(id=None):
    form = MovieForm()
    form.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]
    movie = Movie.query.get_or_404(int(id))
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
        form.title.data = movie.title
        form.area.data = movie.area
        form.length.data = movie.lenght

    if form.validate_on_submit():
        data = form.data
        form.url.validators = []
        form.logo.validators = []
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        if movie_count == 1 and movie.title != data["title"]:
            flash("片名已经存在", "err")
            return redirect(url_for("admin.movie_edit", id=id))

        if not os.path.exists(app.config["UP_DIR"]):
            os.chmod(app.config["UP_DIR"], "rw")
            os.makedirs(app.config["UP_DIR"])

        if form.url.data.filename != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)

        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)

        movie.star = data["star"]
        movie.tag_id = data["tag_id"]
        movie.info = data["info"]
        movie.title = data["title"]
        movie.lenght = data["lenght"]
        movie.release_time = data["release_time"]
        db.session.add(movie)
        db.session.commit()
        flash("修改电影成功", "ok")
        util.InsertOplog("修改电影成功:" + movie.title)
        return redirect(url_for("admin.movie_edit", id=id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


@admin.route("/preview/add/", methods=['GET', 'POST'])
@admin_login_req
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.chmod(app.config["UP_DIR"], "rw")
        logourl = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logourl)
        preview = Preview(
            title=data["title"],
            logo=logourl
        )
        db.session.add(preview)
        db.session.commit()
        flash("电影预告添加成功", "ok")
        util.InsertOplog("添加电影预告:" + preview.title)
        return redirect(url_for("admin.preview_add"))
    return render_template("admin/preview_add.html", form=form)


@admin.route("/preview/list/<int:page>")
@admin_login_req
def preview_list(page):
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/preview_list.html", page_data=page_data)


@admin.route("/preview/del/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def preview_del(id=None):
    preview = Preview.query.filter_by(id=id).first_or_404()
    filelogo = app.config["UP_DIR"] + preview.logo
    if os.path.exists(filelogo):
        os.remove(filelogo)

    db.session.delete(preview)
    db.session.commit()
    flash("电影预告删除成功", "ok")
    util.InsertOplog("删除电影预告:" + preview.title)
    return redirect(url_for('admin.preview_list', page=1))


@admin.route("/preview/edit/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def preview_edit(id=None):
    form = PreviewForm()
    preview = Preview.query.get_or_404(int(id))
    if request.method == "GET":
        form.title.data = preview.title

    if form.validate_on_submit():
        data = form.data
        form.logo.validators = []
        preview_count = Preview.query.filter_by(title=data["title"]).count()
        if preview_count == 1 and preview.title != data["title"]:
            flash("电影预告名已经存在", "err")
            return redirect(url_for("admin.preview_edit", id=id))

        if not os.path.exists(app.config["UP_DIR"]):
            os.chmod(app.config["UP_DIR"], "rw")
            os.makedirs(app.config["UP_DIR"])

        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + preview.logo)

        preview.title = data["title"]
        db.session.add(preview)
        db.session.commit()
        flash("修改电影预告成功", "ok")
        util.InsertOplog("修改电影预告:" + preview.title)
        return redirect(url_for("admin.preview_edit", id=id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


@admin.route("/user/list/<int:page>/")
@admin_login_req
def user_list(page):
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.id
    ).paginate(page=page, per_page=10)
    return render_template("admin/user_list.html", page_data=page_data)


@admin.route("/user/view/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def user_view(id):
    form = UserForm()
    user = User.query.get_or_404(int(id))
    form.id = user.id
    form.name = user.name
    form.email = user.email
    form.phone = user.phone
    form.face = user.face
    form.addtime = user.addtime
    form.uuid = user.uuid
    form.info = user.info
    return render_template("admin/user_view.html", form=form)


@admin.route("/user/del/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def user_del(id):
    user = User.query.filter_by(id=id).first_or_404()
    faceurl = app.config["UP_DIR"] + user.face
    if os.path.exists(faceurl):
        os.remove(faceurl)

    db.session.delete(user)
    db.session.commit()
    flash("用户删除成功", "ok")
    util.InsertOplog("修改用户:" + user.title)
    return redirect(url_for('admin.user_list', page=1))


@admin.route("/comment/list/<int:page>", methods=['GET', 'POST'])
@admin_login_req
def comment_list(page):
    if page is None:
        page = 1
    page_data = Comment.query.join(Movie).join(User).filter(
        Comment.movie_id == Movie.id, Comment.user_id == User.id)\
        .order_by(Comment.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/comment_list.html", page_data=page_data)

@admin.route("/comment/del/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def comment_del(id):
    comment = Comment.query.filter_by(id=id).first_or_404()
    db.session.delete(comment)
    db.session.commit()
    flash("电影评论删除成功", "ok")
    util.InsertOplog("删除电影评论:" + comment.content)
    return redirect(url_for('admin.comment_list', page=1))


@admin.route("/moviecol/list/<int:page>", methods=['GET', 'POST'])
@admin_login_req
def moviecol_list(page):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(Movie).join(User).\
            filter(Moviecol.movie_id == Movie.id, Moviecol.user_id == User.id).\
            order_by(Moviecol.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/moviecol_list.html",page_data = page_data)

@admin.route("/moviecol/del/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def moviecol_del(id):
    moviecol = Moviecol.query.filter_by(id=id).first_or_404()
    db.session.delete(moviecol)
    db.session.commit()
    flash("电影收藏删除成功", "ok")
    util.InsertOplog("删除电影收藏:" + moviecol.content)
    return redirect(url_for('admin.moviecol_list', page=1))


@admin.route("/oplog/list/<int:page>/", methods=['GET', 'POST'])
@admin_login_req
def oplog_list(page = None):
    if page is None:
        page = 1
    page_data = Oplog.query.join(Admin).filter(Admin.id == Oplog.admin_id).order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/oplog_list.html",page_data=page_data)


@admin.route("/adminloginlog/list/<int:page>/", methods=['GET', 'POST'])
@admin_login_req
def adminloginlog_list(page = None):
    if page is None:
        page = 1
    page_data = Adminlog.query.join(Admin).filter(Admin.id == Adminlog.admin_id).order_by(
        Adminlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/adminloginlog_list.html",page_data=page_data)


@admin.route("/userloginlog/list/<int:page>/", methods=['GET', 'POST'])
@admin_login_req
def userloginlog_list(page = None):
    if page is None:
        page = 1
    page_data = Userlog.query.join(User).filter(User.id == Userlog.user_id).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/userloginlog_list.html",page_data=page_data)


@admin.route("/role/add/", methods=['GET', 'POST'])
@admin_login_req
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        form.auths.choices = [(v.id, v.name) for v in Auth.query.all()]
        data = form.data
        role = Role(
            name = data["name"],
            auths = ",".join(map(lambda v:str(v),data["auths"]))
        )
        db.session.add(role)
        db.session.commit()
        flash("添加角色成功","ok")
        redirect(url_for("admin.role_add"))
    return render_template("admin/role_add.html",form = form)


@admin.route("/role/list/<int:page>",methods=['GET'])
@admin_login_req
def role_list(page = None):
    if page is None:
        page = 1
    page_data = Role.query.order_by(Role.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/role_list.html",page_data=page_data)

@admin.route("/role/edit/<int:id>",methods=['GET','POST'])
@admin_login_req
def role_edit(id):
    form = RoleForm()
    role = Role.query.get_or_404(int(id))
    if request.method == "GET":
        form.auths.data = list(map(lambda v:int(v), role.auths.split(",")))
        form.name.data = role.name
    if form.validate_on_submit():
        data = form.data
        role.name = data["name"]
        role.auths = ",".join(map(lambda v:str(v),data["auths"]))
        db.session.add(role)
        db.session.commit()
        flash("修改角色成功", "ok")
        util.InsertOplog("修改角色成功:"+role.name+"-"+role.auths)
        return redirect(url_for("admin.role_list",page = 1))
    return render_template("admin/role_edit.html",form = form)


@admin.route("/role/del/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def role_del(id):
    role = Role.query.filter_by(id=id).first_or_404()
    db.session.delete(role)
    db.session.commit()
    flash("角色删除成功", "ok")
    util.InsertOplog("删除角色成功:" + role.name)
    return redirect(url_for('admin.role_list', page=1))

@admin.route("/auth/add/", methods=['GET', 'POST'])
@admin_login_req
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name = data["name"],
            url = data["url"]
        )
        db.session.add(auth)
        db.session.commit()
        flash("权限添加成功","ok")
        util.InsertOplog("权限添加成功:"+data["name"])
        return redirect(url_for('admin.auth_list',page = 1))
    return render_template("admin/auth_add.html",form = form)


@admin.route("/auth/list/<int:page>",methods=['GET', 'POST'])
@admin_login_req
def auth_list(page = None):
    if page is None:
        page = 1
    page_data = Auth.query.order_by(Auth.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/auth_list.html",page_data = page_data)

@admin.route("/auth/del/<int:id>" ,methods=['GET', 'POST'])
@admin_login_req
def auth_del(id):
    auth = Auth.query.filter_by(id=id).first_or_404()
    db.session.delete(auth)
    db.session.commit()
    flash("权限删除成功", "ok")
    util.InsertOplog("权限删除成功:" + auth.name)
    return redirect(url_for('admin.auth_list', page=1))


@admin.route("/auth/edit/<int:id>",methods=['GET', 'POST'])
@admin_login_req
def auth_edit(id):
    form = AuthForm()
    auth = Auth.query.filter_by(id=id).first_or_404()
    if request.method == "GET":
        form.name.data = auth.name
        form.url.data = auth.url

    if form.validate_on_submit():
        data = form.data
        auth.url = data["url"]
        db.session.add(auth)
        db.session.commit()
        flash("权限修改成功", "ok")
        util.InsertOplog("权限修改成功:" + auth.url)
        return redirect(url_for('admin.auth_list', page=1))
    return render_template("admin/auth_edit.html", form=form)



@admin.route("/admin/add/",methods=['GET', 'POST'])
@admin_login_req
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        form.role_id.choices = [(v.id, v.name) for v in Role.query.all()]
        data=form.data
        admin = Admin(
            name=data["name"],
            pwd=data["pwd"],
            role_id = data["role_id"]
        )
        db.session.add(admin)
        db.session.commit()
        flash("管理员创建成功","ok")
        util.InsertOplog("管理员创建成功"+data["name"])
        return redirect(url_for('admin.admin_list', page=1))
    return render_template("admin/admin_add.html",form = form)


@admin.route("/admin/list/<int:page>/",methods=['GET', 'POST'])
@admin_login_req
def admin_list(page = None):
    if page is None:
        page = 1

    page_data = Admin.query.join(Role).filter( Admin.role_id == Role.id ).order_by(
        Admin.addtime.desc()
    ).paginate( page=page, per_page=10 )

    return render_template("admin/admin_list.html",page_data=page_data)