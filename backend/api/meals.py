import flask

import models

routes = flask.blueprints.Blueprint('meals', __name__, url_prefix='/meals') 


@routes.route('/', methods=['GET'])
def get_all_meals() -> flask.Response:
    return models.Meal.get_meals(), 200


@routes.route('/<string:id>', methods=['GET'])
def get_user_meals(id: str) -> flask.Response:
    return models.User.get_meals(int(id)), 200


@routes.route('/<string:id>', methods=['POST'])
def save_user_meal(id: str) -> flask.Response:
    body = flask.request.json
    result = models.User.save_meal(int(id), body)
    if result:
        return 'SUCCESS', 200
    else:
        return 'FAILED', 400


@routes.route('/<string:id>', methods=['PUT'])
def update_user_meal(id: str) -> flask.Response:
    body = flask.request.json
    result = models.User.update_meal(int(id), body)
    if result:
        return 'SUCCESS', 200
    else:
        return 'FAILED', 400


@routes.route('/<string:id>', methods=['DELETE'])
def delete_user_meal(id: str) -> flask.Response:
    body = flask.request.json
    result = models.User.delete_meal(int(id), body)
    if result:
        return 'SUCCESS', 200
    else:
        return 'FAILED', 400