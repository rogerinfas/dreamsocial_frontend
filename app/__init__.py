from flask import Flask, render_template, current_app
from .routes import home, users, profiles, auth, posts
from requests.exceptions import ConnectionError, Timeout, RequestException
import os
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Configurar clave secreta para sesiones
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Registrar filtros personalizados para Jinja2
    @app.template_filter('strftime')
    def strftime_filter(date_string, format='%d/%m/%Y %H:%M'):
        """Filtro para formatear fechas en templates"""
        if isinstance(date_string, str):
            # Convertir string ISO a datetime
            try:
                # Manejar diferentes formatos de fecha
                if 'T' in date_string:
                    # Formato ISO con T
                    if date_string.endswith('Z'):
                        date_string = date_string[:-1] + '+00:00'
                    if '.' in date_string:
                        # Con microsegundos
                        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                    else:
                        # Sin microsegundos
                        dt = datetime.fromisoformat(date_string)
                else:
                    # Formato simple
                    dt = datetime.fromisoformat(date_string)
                return dt.strftime(format)
            except (ValueError, TypeError):
                return date_string
        elif isinstance(date_string, datetime):
            return date_string.strftime(format)
        else:
            return str(date_string)

    # Hacer current_app disponible en todos los templates
    @app.context_processor
    def inject_current_app():
        return dict(current_app=current_app)

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
