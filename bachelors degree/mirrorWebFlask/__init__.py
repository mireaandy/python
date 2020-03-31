from flask import Flask, render_template
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
