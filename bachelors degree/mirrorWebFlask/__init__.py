from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from mirrorWebFlask.configuration import Config
from mirrorWebFlask.forms import LoginForm


app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', message="Welcome")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        return render_template('index.html', message=form.username.data)

    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
