from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    with app.app_context():
        # 註冊路由
        from . import routes
        app.register_blueprint(routes.bp)

        return app
