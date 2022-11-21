# -----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# -----------------------------------------------------------------------------------------
import os

from dotenv import dotenv_values, find_dotenv, load_dotenv
import flask

import api
import models
from spaces import upload_file, get_file_url, download_file


def _get_env():
    return os.getenv('CHOSEN_ENV')


_ENV_FILE_NAMES = {'PROD': '.env', 'DEV': '.env.dev'}


class EnvNames:
    DEV = 'DEV'
    PROD = 'PROD'


# Download env file from spaces
if _get_env() == EnvNames.PROD:
    download_file(filename=_ENV_FILE_NAMES[os.getenv('CHOSEN_ENV')])

load_dotenv(find_dotenv(_ENV_FILE_NAMES[_get_env()]))

_env = {**dotenv_values(find_dotenv(_ENV_FILE_NAMES[_get_env()]))}


def create_app():
    app = flask.Flask(__name__)

    if _get_env() == EnvNames.DEV:
        from flask_cors import CORS
        CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = _env.get('MYSQL_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['UPLOAD_FOLDER'] = _UPLOAD_FOLDER
    models.db.init_app(app)
    with app.app_context():
        models.db.create_all()

    return app


app = create_app()
app.register_blueprint(api.routes)


@app.route('/')
def index():
    return app.send_static_file('index.html')
