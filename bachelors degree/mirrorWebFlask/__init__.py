from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from google_auth_oauthlib.flow import Flow
import pickle
import configuration
import forms



app = Flask(__name__)

app.config.from_object(configuration.Config)

database = SQLAlchemy(app)
migrate = Migrate(app, database)
login = LoginManager(app)
flow = Flow.from_client_secrets_file('credentials.json', app.config['GOOGLE_SCOPES'])


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
    googleToken = database.Column(database.String(1000), index=False, unique=True, nullable=True)
    pictures = database.relationship('UserPicture', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"{self.username} {self.newsTopic}"

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


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main'))

    form = forms.LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('index'))

        login_user(user, remember=form.remember_me.data)

        return redirect(url_for('main'))

    return render_template('index.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = forms.RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, newsTopic=form.newsTopic.data, isActive='0')

        user.set_password(form.password.data)
        database.session.add(user)
        database.session.commit()

        return redirect(url_for('index'))

    return render_template('signup.html', title='Register', form=form)


@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')


@app.route('/google', methods=['GET', 'POST'])
def google():
    flow.redirect_uri = 'http://raspberry.tplinkdns.com:276/google'

    if 'code' not in request.args:
        auth_uri, _ = flow.authorization_url()

        return redirect(auth_uri)
    else:
        flow.fetch_token(code=request.values['code'])

        user = User.query.filter_by(username=current_user.username).first()
        user.googleToken = 'credentials/' + current_user.username
        database.session.commit()

        pickle.dump(flow.credentials, open('../credentials/'+current_user.username, mode='wb'))
        #current_user.googleToken = flow.credentials

        return redirect(url_for('main'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=276)
