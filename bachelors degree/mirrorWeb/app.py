from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap
from google_auth_oauthlib.flow import Flow
import configuration
import pickle
import os

app = Flask(__name__)

app.config.from_object(configuration.Config)

database = SQLAlchemy(app)
migrate = Migrate(app, database)
login = LoginManager(app)
bootstrap = Bootstrap(app)
flow = Flow.from_client_secrets_file('credentials.json', app.config['GOOGLE_SCOPES'])
flow.redirect_uri = app.config['REDIRECT_URI']

import forms
import models

@login.user_loader
def load_user(userId):
    return models.User.query.get(int(userId))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main'))

    form = forms.LoginForm()

    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('index'))

        login_user(user, remember=form.remember_me.data)

        return redirect(url_for('main'))

    return render_template('index.html', form=form, index=True)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = forms.RegistrationForm()

    if form.validate_on_submit():
        user = models.User(username=form.username.data, isActive='0')

        user.set_password(form.password.data)
        database.session.add(user)
        database.session.commit()

        return redirect(url_for('index'))

    return render_template('signup.html', title='Register', form=form, signup=True)


@app.route('/main', methods=['GET', 'POST'])
@login_required
def main():
    form = forms.EditForm()

    if form.is_submitted():
        user = models.User.query.filter_by(username=current_user.username).first()

        if form.newsTopic.data != user.newsTopic and form.newsTopic.data is not None:
            user.newsTopic = form.newsTopic.data
            database.session.commit()

        if 'files[]' in request.files:
            files = request.files.getlist('files[]')

            for file in files:
                if file and allowed_file(file.filename):
                    filename = user.username + str(app.config['PICTURE_ID_FILENAME']) + '.' + \
                               file.filename.rsplit('.', 1)[1].lower()
                    filepath = os.path.join(app.config['PICTURE_FOLDER'], filename)

                    file.save(filepath)

                    pic = models.UserPicture(userId=user.id, picturePath=filepath, encoded=0)

                    database.session.add(pic)
                    database.session.commit()

                    app.config['PICTURE_ID_FILENAME'] += 1

        if form.changePassword.data:
            return redirect(url_for('confirmpass'))

        return render_template('main.html', form=form, main=True, changed=True)

    return render_template('main.html', form=form, main=True)


@app.route('/confirmpass.html', methods=['GET', 'POST'])
@login_required
def confirmpass():
    form = forms.ConfirmPassForm()
    user = models.User.query.filter_by(username=current_user.username).first()

    if form.validate_on_submit():
        if user.check_password(form.currentPassword.data):
            user.set_password(form.newPassword.data)
            database.session.commit()

            return redirect(url_for('main'))
        else:
            form.currentPassword.errors.append('Wrong password')

    return render_template('confirmpass.html', form=form, chnpass=True)


@login.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('index'))


@app.route('/google', methods=['GET', 'POST'])
@login_required
def google():
    if 'code' not in request.args:
        auth_uri, _ = flow.authorization_url()
        return redirect(auth_uri)

    else:
        user = models.User.query.filter_by(username=current_user.username).first()

        if not user.googleToken:
            flow.fetch_token(code=request.values['code'])

            user.googleToken = app.config['PROJECT_PATH'] + '/config/userCredentials/' + current_user.username

            database.session.commit()
            pickle.dump(flow.credentials, open(user.googleToken, mode='wb'))

        return redirect(url_for('main'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index', index=True))


if __name__ == '__main__':
    app.run()
