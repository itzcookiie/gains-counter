from flask import blueprints

from api import meals

routes = blueprints.Blueprint('api_routes', __name__, url_prefix='/api/v1')
routes.register_blueprint(meals.routes)