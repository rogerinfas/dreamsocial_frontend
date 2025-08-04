from flask import Flask, render_template
from .routes import home, users, profiles, auth, posts
from requests.exceptions import ConnectionError, Timeout, RequestException
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Configurar clave secreta para sesiones
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Registrar blueprints
    app.register_blueprint(home.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(profiles.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(posts.bp)

    # Error handler para problemas de conexión con el backend
    @app.errorhandler(ConnectionError)
    @app.errorhandler(Timeout)
    @app.errorhandler(RequestException)
    def handle_backend_error(error):
        return render_template('errors/503.html', error=error), 503

    return app
