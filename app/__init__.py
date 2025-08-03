from flask import Flask, render_template
from .routes import home, users, profiles
from requests.exceptions import ConnectionError, Timeout, RequestException

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Registrar blueprints
    app.register_blueprint(home.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(profiles.bp)

    # Error handler para problemas de conexión con el backend
    @app.errorhandler(ConnectionError)
    @app.errorhandler(Timeout)
    @app.errorhandler(RequestException)
    def handle_backend_error(error):
        return render_template('errors/503.html', error=error), 503

    return app
