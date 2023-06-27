#!/Anaconda3/python
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

from .app import app
db = SQLAlchemy(app)


def key_gen(user: str, version: str) -> int:
    """
    :param user: the username issuing any command is stored in the etl id source table
    :param version: the software version employed by the command at the time
    :return etl_id: the unique ID created for this job
    """
    staged_key_record = {
        "id_created_ts": datetime.now(),
        "user": user,
        "version": version
    }
    etl_id_source_record = ETLIDSource(**staged_key_record)
    db.session.add(etl_id_source_record)
    db.session.commit()
    db.session.refresh(etl_id_source_record)
    etl_id = etl_id_source_record.etl_id

    return etl_id


class Batch(db.Model, SerializerMixin):  # the record of API requests
    __tablename__ = "batch"
    batch_id = db.Column(db.BigInteger, primary_key=True)
    batch_action = db.Column(db.Text, nullable=False)
    batch_status = db.Column(db.Text, nullable=False)


class Process(db.Model, SerializerMixin):  # the record of processes spawned by API requests
    __tablename__ = "process"
    proc_id = db.Column(db.BigInteger, primary_key=True)
    batch_id = db.Column(db.BigInteger)
    transaction_key = db.Column(db.Text, index=True)
    proc_record_id = db.Column(db.BigInteger)
    proc_status = db.Column(db.Text, nullable=False)
    row = db.Column(db.BigInteger)
    foreign_record_id = db.Column(db.Text)


class ETLIDSource(db.Model, SerializerMixin):  # the source table for all primary keys, preserving request meta-data
    __tablename__ = "etl_id_source"
    etl_id = db.Column(db.BigInteger, primary_key=True)
    user = db.Column(db.Text)
    version = db.Column(db.Text)
    id_created_ts = db.Column(db.DateTime)
