import flask

import models

routes = flask.blueprints.Blueprint('meals', __name__, url_prefix='/meals') 


@routes.route('/', methods=['GET'])
def get_all_meals() -> flask.Response:
    return models.Meal.get_meals(), 200


@routes.route('/<int:user_id>', methods=['GET'])
def get_user_meals(user_id: int) -> flask.Response:
    return models.User.get_meals(user_id), 200


@routes.route('/<int:user_id>', methods=['POST'])
def save_user_meal(user_id: int) -> flask.Response:
    body = flask.request.json
    result = models.User.save_meal(user_id, body)
    if result:
        return {'result': 'SUCCESS'}, 200
    else:
        return {'result': 'FAILED'}, 400


@routes.route('/<string:id>', methods=['PUT'])
def update_user_meal(id: str) -> flask.Response:
    body = flask.request.json
    result = models.User.update_meal(int(id), body)
    if result:
        return {'result': 'SUCCESS'}, 200
    else:
        return {'result': 'FAILED'}, 400


@routes.route('/<string:id>', methods=['DELETE'])
def delete_user_meal(id: str) -> flask.Response:
    body = flask.request.json
    result = models.User.delete_meal(int(id), body)
    if result:
        return {'result': 'SUCCESS'}, 200
    else:
        return {'result': 'FAILED'}, 400