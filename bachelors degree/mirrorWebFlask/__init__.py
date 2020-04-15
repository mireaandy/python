from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
import configuration
import forms



app = Flask(__name__)

app.config.from_object(configuration.Config)

database = SQLAlchemy(app)
migrate = Migrate(app, database)
login = LoginManager(app)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, database.Model):

    __tablename__ = 'userData'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(100), index=False, unique=True, nullable=False)
    password = database.Column(database.String(128), index=False, unique=False, nullable=False)
    newsTopic = database.Column(database.String(50), index=False, unique=False, nullable=True)
    isActive = database.Column(database.String(1), index=False, unique=False, nullable=False)
    pictures = database.relationship('UserPicture', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"{self.usermane} {self.newsTopic}"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class UserPicture(database.Model):

    __tablename__ = 'userPictures'
    userId = database.Column(database.Integer, database.ForeignKey('userData.id'))
    pictureId = database.Column(database.Integer, primary_key=True)
    picturePath = database.Column(database.String(100), index=False, unique=True, nullable=False)

    def __repr__(self):
        return f"{self.pictureId} {self.userId}"


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', message="Welcome")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        return render_template('index.html', message=form.username.data)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
