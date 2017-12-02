import base64
from functools import wraps

from pyinfraboxutils import get_logger
from pyinfraboxutils.db import DB
from pyinfraboxutils.token import decode

from flask import Flask, g, jsonify, request, abort
app = Flask(__name__)

logger = get_logger('ibflask')

def get_token():
    auth = dict(request.headers).get('Authorization', None)

    if not auth:
        logger.warn('No auth header')
        abort(401, 'Unauthorized')

    if auth.startswith("Basic "):
        auth = auth.split(" ")[1]

        try:
            decoded = base64.b64decode(auth)
        except:
            logger.warn('could not base64 decode auth header')
            abort(401, 'Unauthorized')

        s = decoded.split('infrabox:')

        if len(s) != 2:
            logger.warn('Invalid auth header format')
            abort(401, 'Unauthorized')

        try:
            token = decode(s[1])
        except Exception as e:
            logger.exception(e)
            abort(401, 'Unauthorized')

        return token
    elif auth.startswith("token "):
        token = auth.split(" ")[1]

        try:
            token = decode(token)
        except Exception as e:
            logger.exception(e)
            abort(401, 'Unauthorized')

        return token
    else:
        logger.warn('Invalid auth header format')
        abort(401, 'Unauthorized')

@app.before_request
def before_request():
    g.db = DB()

@app.teardown_request
def teardown_request(_):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': error.description, 'status': 404}), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'message': error.description, 'status': 401}), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': error.description, 'status': 400}), 400

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.token = get_token()
        return f(*args, **kwargs)

    return decorated_function

def job_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token()

        if token['type'] != 'job':
            logger.warn('token type is not job but "%s"', token['type'])
            abort(401, 'Unauthorized')

        job_id = token['job']['id']
        r = g.db.execute_one('''
            SELECT state, project_id, name
            FROM job
            WHERE id = %s''', [job_id])

        if not r:
            logger.warn('job not found')
            abort(401, 'Unauthorized')

        job_state = r[0]
        if job_state not in ('queued', 'running', 'scheduled'):
            logger.warn('job not in an active state')
            abort(401, 'Unauthorized')


        token['job']['state'] = r[0]
        token['job']['name'] = r[2]
        token['project'] = {}
        token['project']['id'] = r[1]
        g.token = token

        return f(*args, **kwargs)

    return decorated_function