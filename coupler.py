#!/Anaconda3/python
from incoming import datatypes, PayloadValidator

from .model import MODEL_MAP


class RecordIDValidator(PayloadValidator):
    record_id = datatypes.Integer(required=True)
    user = datatypes.String(required=True)


COUPLER = {
    'batch': {
        'model': MODEL_MAP['batch'],
        'processor': None,
        'validator': RecordIDValidator,
        'methods': ['GET'],
    },
    'process': {
        'model': MODEL_MAP['process'],
        'processor': None,
        'validator': RecordIDValidator,
        'methods': ['GET'],
    },
    'etl_id_source': {
        'model': MODEL_MAP['etl_id_source'],
        'processor': None,
        'validator': RecordIDValidator,
        'methods': ['GET'],
    },
}
