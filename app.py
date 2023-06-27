#!/Anaconda3/python
from datetime import datetime
from flask import Flask
import os

from .database import refresh_request
from .logger import mylogger

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/landing', methods=['GET', 'POST'])
def landing():
    if not session.get('logged_in'):
        session.clear()
        return redirect(url_for('login', now=datetime.utcnow()))
    if postrequest.method == 'POST':
        route = postrequest.form['submit'].lower()
        mylogger.info(f"{session['user_name']} SELECTS ROUTE: {route}")
        if route == 'logout':
            route = 'login'

        return redirect(url_for(route, now=datetime.utcnow()))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate a user session"""
    TABLE = ''  # implement your model
    error = None
    session['bodyclass'] = "default"
    if session:
        session.clear()
    if postrequest.method == 'POST':
        request = refresh_request()
        user_name = postrequest.form['username']
        user_password = postrequest.form['password']
        sql = "SELECT * FROM {TABLE} WHERE username = %s AND user_password = %s"
        data = (user_name, user_password)  # implement your own encryption/decryption scheme on the pw
        response = request.query(sql, data)
        if len(response) > 0:
            role = response[0]['user_role']
            session['role'] = role
            session['user_name'] = user_name
            session['user_id'] = response[0]['user_id']
            session['logged_in'] = True
            mylogger.info(f'{user_name} logs in')
            roles = {  # route account-holders to different places with role-based access
                1: 'levelone',  # each of these must be a valid app route name
                2: 'leveltwo',
                3: 'levelthree'
            }
            return redirect(url_for(roles[role], now=datetime.utcnow()))
        else:
            error = 'Login Failed'
            attempted_user = postrequest.form['username']
            mylogger.warning(f"{attempted_user} : {error}")
    
    return render_template('login.html', now=datetime.utcnow(), error=error)


@app.route("/")
def hello():
    return redirect(url_for('login', now=datetime.utcnow()))
