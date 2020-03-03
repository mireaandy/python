from flask import *
from sqlite3 import *
from pathlib import Path


app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        if request.form["topicSubmit"] == "submitTopic":
            connection = connect("../mirrorDatabase.db")
            cursor = connection.cursor()

            cursor.execute("INSERT INTO userData VALUES('2', '{}')".format(request.form['topic']))
            connection.commit()
            cursor.close()

    return render_template('index.html')


if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)