from datetime import datetime
from flask import (
    Flask,
    redirect,
    request as postrequest,
    session,
    )
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from sqlalchemy.sql.expression import true
from sqlalchemy_serializer import SerializerMixin
import string
import sys
import validators

import __auth__ as auth
from __version__ import version

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


class Clicks(db.Model, SerializerMixin):
    __tablename__ = "clicks"
    etl_id = db.Column(db.Text, primary_key=True)
    member_id = db.Column(db.Text)
    url_key = db.Column(db.Text)


class ETLIDSource(db.Model, SerializerMixin):
    __tablename__ = "etl_id_source"
    etl_id = db.Column(db.BigInteger, primary_key=True)
    user = db.Column(db.BigInteger)
    version = db.Column(db.Text)
    id_created_ts = db.Column(db.DateTime)


class URL(db.Model, SerializerMixin):
    __tablename__ = "url"
    url_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, unique=True, index=True)
    target_url = db.Column(db.Text, index=True)
    account_id = db.Column(db.BigInteger)
    expiration_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean)
    clicks = db.Column(db.Integer, default=0)


def key_gen(user: int, vers: str) -> int:
    """
    This function is employed wherever a new record is staged for insertion
    User, version, and timestamp metadata are inserted into the ETLIDSource,
    this insertion provides the auto-incremented ID which is what's returned
    :param user: the username issuing the command
    :param vers: the software version employed at the time
    :return etl_id: the unique ID created for this job
    """
    staged_key_record = {
        "id_created_ts": datetime.now(),
        "user": user,
        "version": vers
    }
    etl_id_source_record = ETLIDSource(**staged_key_record)  # type: ignore
    db.session.add(etl_id_source_record)
    db.session.commit()
    db.session.refresh(etl_id_source_record)

    return etl_id_source_record.etl_id


def get_db_url_by_key(url_key: str):
    """
    Select a URL record by its url key
    :param url_key: the shortened/unique key to select by
    """
    return (
        db.session.query(URL).filter(
            URL.key == url_key,
            URL.is_active == true()
        ).first()
    )


def create_random_key(length: int = 5) -> str:
    """
    Use letters and digits to create a random key
    :param length: the desired character-length of the output
    """
    chars = string.ascii_uppercase + string.digits

    return "".join(secrets.choice(chars) for _ in range(length))


def post_url(long_url: str, expiration_date=None):
    """
    Encode a URL as a 5-short url @ HOST/
    :param long_url: the url to be encoded
    :param expiration_date: the date on which to sweep this URL
    """
    if not validators.url(long_url):
        print(f'{long_url} is not a valid URL', file=DEBUG_ROUTE)
        return None
    protocol = 'https://'
    well_formed = False
    while not well_formed:
        try:
            if long_url.index(protocol) == 0:
                well_formed = True
        except ValueError:
            long_url = f'{protocol}{long_url}'
    key = create_random_key()
    while get_db_url_by_key(key):
        key = create_random_key()
    staged_url_record = {
        'key': key,
        'target_url': long_url,
        'expiration_date': expiration_date,
        'account_id': session['account_id']
    }
    url_record = URL(**staged_url_record)  # type: ignore
    db.session.add(url_record)
    db.session.commit()
    db.session.refresh(url_record)

    return url_record.key


def token_post_url(url_key: str, member_id: int):
    """
    encode a shortened URL with member ID as an 8-short url @ HOST/
    :param url_key: the url to be encoded
    :param member_id: an ID of a target member
    """
    token_url = f'{url_key}?source={member_id}'
    key = create_random_key(8)
    while get_db_url_by_key(key):
        key = create_random_key(8)
    url = get_db_url_by_key(key)
    staged_url_record = {
        'key': key,
        'target_url': token_url,
        'expiration_date': url.expiration_date,
        'is_active': True,
        'account_id': session['account_id']
    }
    url_record = URL(**staged_url_record)  # type: ignore
    db.session.add(url_record)
    db.session.commit()
    db.session.refresh(url_record)

    return url_record.key


@app.route("/<url_key>", methods=['GET', 'POST'])
def forward_to_target_url(url_key: str):
    """
    Forward a shortened URL to a target URL
    """
    member_id = postrequest.args.get('source', None)
    if member_id is not None:
        member_id = int(member_id)
    if db_url := get_db_url_by_key(url_key=url_key):
        if member_id is not None:
            staged_click_record = {
                'etl_id': key_gen(member_id, version),
                'member_id': member_id,
                'url_key': url_key
            }
            click_record = Clicks(**staged_click_record)  # type: ignore
            click = db.session.query(Clicks). \
                filter(
                Clicks.member_id == str(member_id),
                Clicks.url_key == url_key
            ).first() is not None
            if not click:
                db.session.add(click_record)
                db.session.commit()
                db_url.clicks += 1
                db.session.commit()
        return redirect(db_url.target_url)
    else:
        pass
        # ToDo: define your error behavior here
