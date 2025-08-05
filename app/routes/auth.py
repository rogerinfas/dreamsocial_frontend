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
        firstName = request.form['firstName']
        lastName = request.form['lastName']

        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/register.html')

        # 1. Registrar el usuario
        user_payload = {'email': email, 'password': password}
        try:
            user_response = requests.post(f"{current_app.config['API_URL']}/auth/register", json=user_payload)
            if user_response.status_code != 201:
                error_data = user_response.json()
                flash(error_data.get('message', 'Error en el registro de usuario.'), 'error')
                return render_template('auth/register.html')
            
            user_data = user_response.json()
            access_token = user_data['access_token']
            user_id = user_data['user']['id']

            # 2. Crear el perfil
            profile_payload = {
                'firstName': firstName,
                'lastName': lastName,
                'userId': user_id
            }
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = requests.post(f"{current_app.config['API_URL']}/profiles", json=profile_payload, headers=headers)

            if profile_response.status_code != 201:
                # Aquí se podría manejar la eliminación del usuario si la creación del perfil falla,
                # pero por ahora solo mostraremos un error.
                flash('Se creó el usuario, pero hubo un error al crear el perfil.', 'error')
                return render_template('auth/register.html')

            # 3. Iniciar sesión
            session['access_token'] = access_token
            session['user'] = user_data['user']
            session['logged_in'] = True
            flash('Registro exitoso. ¡Bienvenido!', 'success')
            return redirect(url_for('home.index'))

        except requests.exceptions.RequestException:
            flash('Error de conexión con el servidor.', 'error')

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
