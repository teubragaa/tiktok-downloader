from flask import Flask
from controllers.download_controller import download_controller


def create_app():
    app = Flask(__name__)
    app.register_blueprint(download_controller)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )