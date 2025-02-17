from flask import Flask
from flask_cors import CORS

def create_app():

    app = Flask(__name__)
    CORS(app)

    from app.routes.index import main
    from app.routes.balloons import game
    from app.routes.hand_api import api
    app.register_blueprint(main)
    app.register_blueprint(game)
    app.register_blueprint (api)

    return app