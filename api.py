#!/Anaconda3/python
from flask import jsonify, request
import threading

from .app import app
from .auditor import Auditor
from .coupler import COUPLER
from .model import MODEL_MAP
from .__version__ import version

version = version.replace(".", "")
DEBUG_ROUTE = sys.stderr


def query_records(payload: dict, endpoint='': str) -> list:
    """
    :param payload: a list of key/value constraints to use in filtering
    :param endpoint: a string mapped to the sqla data model of tables
    """
    response = list()
    source_table = MODEL_MAP[endpoint]
    query = source_table.query
    try:
        del payload['user']
    except:
        pass
    for field_name, field_val in payload.items():
        query = query.filter(source_table.__table__.c[field_name] == field_val)
    for row in query.all():
        response.append(row.to_dict())

    return response


def get(payload: dict, endpoint: str) -> dict:
    """
    :param payload: the user-initiated data payload to GET with
    :param endpoint: a string denoting the endpoint invoked
    """
    response = query_records(payload, endpoint=endpoint)
    
    return response


def post(payload: dict, endpoint: str) -> dict:
    """
    :param payload: the user-initiated data payload to POST with
    :param endpoint: a string denoting the endpoint invoked
    """
    user = payload['user']
    processor = COUPLER[endpoint]['processor']
    with Auditor(user, version, endpoint) as job_auditor:
        thread = threading.Thread(target=processor, 
            args=(payload, job_auditor))
        thread.start()
    try:
        batch_key = job_auditor.batch_id
        response = 200
    except AttributeError:
        batch_key = None
        response = 405
    response = {
        "batch_key": batch_key,
        "status": response
    }

    return response


def process_payload():
    response = None
    endpoint = request.endpoint
    method = request.method
    validator = COUPLER[endpoint]['validator']()
    try:
        payload_obj = request.get_json()
    except:
        print("Request is not acceptable JSON", file=DEBUG_ROUTE)
        return jsonify(status=405, response=response)
    result, msg = validator.validate(payload_obj)
    if result:
        if method == "GET":
            response = get(payload_obj, endpoint)
        elif method == "POST":
            response = post(payload_obj, endpoint)
    else:
        print(f"Invalid request payload: {msg}", file=DEBUG_ROUTE)
        return jsonify(status=405, response=msg)
    if response is not None:
        return jsonify(status=200, response=response)
    else:
        print(f"Issue encountered with {method} request", 
            file=DEBUG_ROUTE)
        return jsonify(status=405, response=response)

for endpoint, couplings in COUPLER.items():
    app.add_url_rule(
        f'/api_{version}/{endpoint}',
        endpoint=endpoint, 
        view_func=process_payload,
        methods=couplings['methods']
    )
