#!/Anaconda3/python
from datetime import datetime
import sys

from .logger import mylogger
from .model import (
    db,
    Batch,
    Process,
    key_gen
)


def mint_transaction_key(auditor, row=None, foreign_record_id=None):
    """
    :param auditor: native Auditor class object for data warehousing
    :param row: used when counting rows in tables
    :param foreign_record_id: the primary key from record origin
    """
    ts = datetime.now()
    proc_id = auditor.stamp(row, foreign_record_id)
    transaction_key = auditor.stamp.transaction_key

    return transaction_key, proc_id, auditor.batch_id, auditor.user, ts


class AuditStamp:
    """
    The AuditStamp manages context at the task level.
    """
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
    """
    The Auditor is a context manager at the batch/api-request level.
    """
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
            error_msg = f"{e_type} : {value} : {traceback}"
            mylogger.error(error_msg)
            print(error_msg, file=sys.stderr)
        else:
            # ToDo: wrap QC/exit strategy on activities here
            db.session.query(Batch).filter(Batch.batch_id == self.batch_id).\
                update({Batch.batch_status: "PENDING"}, synchronize_session=False)
            db.session.commit()

        return "ok"

    def __str__(self):
        return f"<Auditor: {self.version}:{self.stamp}>"


def update_status(batch_id, proc_id, message):
    """
    This function is called to log the conclusion of each process in the Process table
    """
    
    db.session.query(Process). \
        filter(Process.batch_id == batch_id, Process.proc_id == proc_id). \
        update({Process.proc_status: message}, synchronize_session=False)
    db.session.commit()
    batch_check_query = db.session.query(Process). \
        filter(Process.batch_id == batch_id, Process.proc_status == 'PENDING')
    if len(batch_check_query.all()) == 0:
        db.session.query(Batch).filter(Batch.batch_id == batch_id).\
            update({Batch.batch_status: "COMPUTED"}, synchronize_session=False)
        db.session.commit()
