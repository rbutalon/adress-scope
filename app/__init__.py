from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_mapping(API_TIMEOUT=8)
    app.json.sort_keys = False
    if test_config:
        app.config.update(test_config)

    from .routes import main
    app.register_blueprint(main)
    return app
