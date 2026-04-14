from flask import Flask

from app.routes import bp as main_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static",
    )
    app.config.from_object("app.config.Config")
    app.register_blueprint(main_bp)
    return app
