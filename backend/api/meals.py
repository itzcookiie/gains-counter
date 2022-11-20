from flask import blueprints

import models

routes = blueprints.Blueprint('meals', __name__) 


@routes.route('/')
def get_meals():
    pass