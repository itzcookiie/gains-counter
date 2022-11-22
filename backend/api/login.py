import flask

from api.response_types import ResultCode
import models

routes = flask.blueprints.Blueprint('login', __name__, url_prefix='/login') 


@routes.route('/', methods=['POST'])
def login():
    body = flask.request.json
    user = body['user']
    results_msg, results = models.User(username=user['username']).save()
    result_msg_value = results_msg.value
    if not results:
        return {
            'result_code': ResultCode.LOGIN_FAILED.value,
            'result_message': result_msg_value
        }, 400
    return {
        'result_code': ResultCode.LOGIN_SUCCESS.value,
        'result_message': result_msg_value
    }, 200