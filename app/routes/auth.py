from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import requests

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        payload = {
            'email': email,
            'password': password
        }
        
        try:
            response = requests.post(f"{current_app.config['API_URL']}/auth/login", json=payload)
            
            if response.status_code == 201:
                data = response.json()
                # Guardar token y datos del usuario en la sesión
                session['access_token'] = data['access_token']
                session['user'] = data['user']
                session['logged_in'] = True
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('home.index'))
            else:
                error_data = response.json()
                flash(error_data.get('message', 'Error en el inicio de sesión'), 'error')
        except requests.exceptions.RequestException:
            flash('Error de conexión con el servidor', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/register.html')
        
        payload = {
            'email': email,
            'password': password
        }
        
        try:
            response = requests.post(f"{current_app.config['API_URL']}/auth/register", json=payload)
            
            if response.status_code == 201:
                data = response.json()
                # Guardar token y datos del usuario en la sesión
                session['access_token'] = data['access_token']
                session['user'] = data['user']
                session['logged_in'] = True
                flash('Registro exitoso', 'success')
                return redirect(url_for('home.index'))
            else:
                error_data = response.json()
                flash(error_data.get('message', 'Error en el registro'), 'error')
        except requests.exceptions.RequestException:
            flash('Error de conexión con el servidor', 'error')
    
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('home.index'))

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_auth_headers():
    """Obtiene los headers de autenticación para las peticiones API"""
    token = session.get('access_token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}
