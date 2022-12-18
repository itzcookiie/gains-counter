import flask

import models

routes = flask.blueprints.Blueprint('results', __name__, url_prefix='/results')


@routes.route('/<int:user_id>/<string:user_date>', methods=['GET'])
def get_all_results(user_id: int):
    return models.User.get_results_for_everyday(user_id), 200
