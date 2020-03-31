from flask import render_template
from mirrorWebFlask import app
from mirrorWebFlask.forms import LoginForm


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)
