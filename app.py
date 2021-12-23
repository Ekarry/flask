import os
from flask import Flask, request, redirect, url_for, render_template, abort
from werkzeug.utils import secure_filename
from flask_autoindex import AutoIndex
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY='666'
)
# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

UPLOAD_FOLDER = os.getenv("DIR", "/home")
USER = os.getenv("USER", "Usver")
TOKEN = os.getenv("TOKEN", "blabla")


# user model
class User(UserMixin):
    def __init__(self, usr_name) -> None:
        self.name = usr_name

    def __repr__(self):
        return "%s" % self.name

    def get_id(self):
        return self.name


files_index = AutoIndex(app, os.path.abspath(UPLOAD_FOLDER), add_url_rules=False)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
tokens = {TOKEN: USER}


def check_token(token):
    if token in tokens:
        return tokens[token]


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        token = request.form["pswd"]
        if check_token(token) is not None:
            user = User(check_token(token))
            login_user(user)
            return redirect(url_for("autoindex"))
        else:
            return abort(401)
    else:
        return render_template("login.html")


@app.route("/files", methods=["POST", "GET"])
@app.route("/files/<path:path>", methods=["POST", "GET"])
@login_required
def autoindex(path="."):
    if request.method == "GET":
        return files_index.render_autoindex(
            path, template_context=dict(SITENAME="Access files")
        )
    else:
        try:
            file = request.files["file"]
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        except:
            pass
        return redirect(url_for("autoindex"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == "__main__":
    app.run(debug=True)
