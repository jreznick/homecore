from datetime import datetime
from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request as postrequest,
    session,
    url_for
)
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy_serializer import SerializerMixin
import sys
from werkzeug.security import check_password_hash

import __auth__ as auth

DEBUG_ROUTE = sys.stderr
app = Flask(__name__)
app.config['SECRET_KEY'] = auth.secret_key
app.config['STATIC_FOLDER'] = f"{os.getenv('APP_FOLDER')}/static"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
USERNAME = auth.username
PASSWORD = auth.password
DBNAME = auth.dbname
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{USERNAME}:{PASSWORD}@localhost:5432/{DBNAME}"
db = SQLAlchemy(app)
endpoints = ['create', 'read', 'update', 'delete']
default_permissions = dict()
for endpoint in endpoints:
    default_permissions[f'/{endpoint}'] = 'DENY'


class Permission(db.Model, SerializerMixin):
    __tablename__ = 'permission'
    permission_id = db.Column(db.BigInteger, primary_key=True)
    permission_name = db.Column(db.Text)
    account_id = db.Column(db.BigInteger)
    role_id = db.Column(db.BigInteger)
    endpoint = db.Column(db.Text)
    permission_level = db.Column(db.Text)
    is_active = db.Column(db.Boolean)
    created_by = db.Column(db.BigInteger)
    created_ts = db.Column(db.DateTime)
    touched_by = db.Column(db.BigInteger)
    touched_ts = db.Column(db.DateTime)


class Role(db.Model, SerializerMixin):
    __tablename__ = 'role'
    role_id = db.Column(db.BigInteger, primary_key=True)
    role_name = db.Column(db.Text, unique=True)
    account_id = db.Column(db.BigInteger)
    is_active = db.Column(db.Boolean)
    created_by = db.Column(db.BigInteger)
    created_ts = db.Column(db.DateTime)
    touched_by = db.Column(db.BigInteger)
    touched_ts = db.Column(db.DateTime)


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    __table_args__ = (
        db.UniqueConstraint(
            'account_id',
            'user_email',
            name='account_email_constraint'
        ),
    )
    user_id = db.Column(db.BigInteger, primary_key=True)
    user_name = db.Column(db.Text, unique=True)
    account_id = db.Column(db.BigInteger)
    password = db.Column(db.Text)
    user_email = db.Column(db.Text)
    user_sms = db.Column(db.BigInteger)
    preferred_contact = db.Column(db.Text)
    is_active = db.Column(db.Boolean)
    role_id = db.Column(db.BigInteger)
    created_by = db.Column(db.BigInteger)
    created_ts = db.Column(db.DateTime)
    touched_by = db.Column(db.BigInteger)
    touched_ts = db.Column(db.DateTime)


def your_privileges(role_id):
    your_privs = dict()
    perms = db.session.query(Permission).filter(
        Permission.role_id == role_id
    ).all()
    for perm in perms:
        your_privs[f'{perm.endpoint}'] = perm.permission_level

    return your_privs


def check_your_privilege(func):
    """Ensure a user is suitably privileged to access a route"""

    @wraps(func)
    def wrapper_perm_check(*args, **kwargs):
        privileges = session.get('privileges')
        if privileges[postrequest.path] == 'DENY':
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return wrapper_perm_check


def login_required(func):
    """Make sure user is logged in before proceeding"""

    @wraps(func)
    def wrapper_login_required(*args, **kwargs):
        if session.get('user_name') is None:
            return redirect(url_for('login', next=postrequest.url))
        return func(*args, **kwargs)

    return wrapper_login_required


@app.route('/create', methods=['GET', 'POST'])
@login_required
@check_your_privilege
def create():
    pass


@app.route('/read', methods=['GET', 'POST'])
@login_required
@check_your_privilege
def read():
    pass


@app.route('/update', methods=['GET', 'POST'])
@login_required
@check_your_privilege
def update():
    pass


@app.route('/delete', methods=['GET', 'POST'])
@login_required
@check_your_privilege
def delete():
    pass


def login():
    now = datetime.now()
    session.clear()
    session['page_title'] = 'Login'
    if postrequest.method == 'POST':
        session.pop('user_name', None)
        user_name = postrequest.form.get('user_name')
        password = postrequest.form.get('password')
        result = False
        exists = db.session.query(User).filter(
            User.user_name == user_name
        ).first() is not None
        if exists:
            user = db.session.query(User).filter(
                User.user_name == user_name
            ).first()
            result = check_password_hash(user.password, password)
        else:
            user = None
        if result:
            session['user_name'] = user.user_name
            session['user_id'] = user.user_id
            session['account_id'] = user.account_id
            session['privileges'] = your_privileges(user.role_id)
            session.pop('_flashes', None)

            return redirect(url_for('req_totp', now=now))
        else:
            flash('Incorrect username and/or password!')

    return render_template('login.html', now=now)
