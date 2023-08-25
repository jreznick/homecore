from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
import sys

from .logger import mylogger
from .version import version

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


class ETLIDSource(db.Model, SerializerMixin):  
    __tablename__ = "etl_id_source"
    etl_id = db.Column(db.BigInteger, primary_key=True)
    user = db.Column(db.Text)
    version = db.Column(db.Text)
    id_created_ts = db.Column(db.DateTime)


class Batch(db.Model, SerializerMixin):  
    __tablename__ = "batch"
    batch_id = db.Column(db.BigInteger, primary_key=True)
    batch_action = db.Column(db.Text, nullable=False)
    batch_status = db.Column(db.Text, nullable=False)


class Process(db.Model, SerializerMixin):  
    __tablename__ = "process"
    proc_id = db.Column(db.BigInteger, primary_key=True)
    batch_id = db.Column(db.BigInteger)
    transaction_key = db.Column(db.Text, index=True)
    proc_record_id = db.Column(db.BigInteger)
    proc_status = db.Column(db.Text, nullable=False)
    row = db.Column(db.BigInteger)
    foreign_record_id = db.Column(db.Text)


def key_gen(user: str, version: str):
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


class AuditStamp:
    def __init__(self, batch_id, user, version):
        self.batch_id = batch_id
        self.user = user
        self.version = version
        self.proc_id = None
        self.record_id = None
        self.row = None

    def __call__(self, row, foreign_record_id):
        self.proc_id = key_gen(self.user, self.version)
        self.row = row
        self.transaction_key = f"{self.batch_id}_{self.proc_id}"
        staged_proc_record = {
            "batch_id": self.batch_id,
            "proc_id": self.proc_id,
            "proc_status": "PENDING",
            "transaction_key": self.transaction_key,
            "row": self.row,
            "foreign_record_id": foreign_record_id
        }
        proc_record = Process(**staged_proc_record)
        db.session.add(proc_record)
        db.session.commit()

        return self.proc_id

    def __str__(self):
        return f"<AuditStamp: \
{self.batch_id}:{self.proc_id}:{self.record_id}:{self.row}:{self.user}>"


class Auditor:
    def __init__(self, user, version, action):
        self.user = user
        self.version = version
        self.action = action
        self.batch_id = key_gen(self.user, self.version)
        staged_batch_record = {
            "batch_id": self.batch_id,
            "batch_action": self.action,
            "batch_status": "STARTING"
        }
        batch_record = Batch(**staged_batch_record)
        db.session.add(batch_record)
        db.session.commit()

    def __enter__(self):
        self.stamp = AuditStamp(self.batch_id, self.user, self.version)

        return self

    def __exit__(self, e_type, value, traceback):
        if e_type is not None:
            print(f"{e_type} : {value} : {traceback}", file=sys.stderr)
            # ToDo: error handler for your app
        else:
            db.session.query(Batch).filter(Batch.batch_id == self.batch_id).\
                update(
                    {Batch.batch_status: "PENDING"}, 
                    synchronize_session=False
                )
            db.session.commit()

        return "ok"

    def __str__(self):
        return f"<Auditor: {self.version}:{self.stamp}>"


def mint_transaction_key(auditor, row=None, foreign_record_id=None):
    ts = datetime.now()
    proc_id = auditor.stamp(row, foreign_record_id)
    transaction_key = auditor.stamp.transaction_key

    return transaction_key, proc_id, auditor.batch_id, ts


def update_status(batch_id: int, proc_id: int, message: str):
    db.session.query(Process). \
        filter(
            Process.batch_id == batch_id, 
            Process.proc_id == proc_id
        ). \
        update(
            {Process.proc_status: message}, 
            synchronize_session=False
        )
    db.session.commit()
    batch_check_query = db.session.query(Process). \
        filter(
            Process.batch_id == batch_id, 
            Process.proc_status == 'PENDING'
        )
    if len(batch_check_query.all()) == 0:
        db.session.query(Batch).filter(Batch.batch_id == batch_id).\
            update(
                {Batch.batch_status: "COMPUTED"}, 
                synchronize_session=False
            )
        db.session.commit()


def my_custom_process(payload: dict, auditor):
    for record in payload['records']:
        # start by minting a transaction key
        transaction_key, proc_id, batch_id, touched_ts = \
            mint_transaction_key(auditor)
        # perform and validate any process here

        # finish by updating your process status with a custom message
        update_status(batch_id, proc_id, f"Batch Action")


def post(payload: dict, endpoint: str):
    user = payload['user']
    # processor = COUPLER[endpoint]['processor']
    processor = my_custom_process
    with Auditor(user, version, endpoint) as job_auditor:
        thread = threading.Thread(
            target=processor,
            args=(payload, job_auditor)
        )
        thread.start()
    try:
        batch_key = job_auditor.batch_id
        status = 200
    except AttributeError:
        batch_key = None
        status = 400
    return {
        "batch_key": batch_key,
        "status": status
    }
