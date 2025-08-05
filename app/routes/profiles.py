from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
import requests
from .auth import get_auth_headers, login_required

bp = Blueprint('profiles', __name__, url_prefix='/profiles')

@bp.route('/')
@login_required
def list_profiles():
    headers = get_auth_headers()
    resp = requests.get(f"{current_app.config['API_URL']}/profiles", headers=headers)

    if resp.status_code == 401:
        flash('Tu sesión ha expirado, por favor inicia sesión de nuevo.', 'error')
        return redirect(url_for('auth.logout'))

    profiles = resp.json() if resp.status_code == 200 else []
    return render_template('profiles/list.html', profiles=profiles)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_profile():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        user_id = request.form.get('userId')

        # Aseguramos que TODO sea string
        form_data = {
            'firstName': str(first_name),
            'lastName': str(last_name),
            'userId': str(user_id)
        }

        files = {}
        if 'avatar' in request.files and request.files['avatar'].filename != '':
            avatar = request.files['avatar']
            files['avatar'] = (avatar.filename, avatar.stream, avatar.mimetype)

        headers = get_auth_headers()
        # Remove content-type from headers for multipart/form-data
        headers.pop('Content-Type', None)

        response = requests.post(
            f"{current_app.config['API_URL']}/profiles",
            data=form_data,
            files=files,
            headers=headers
        )

        if response.status_code == 201:
            return redirect(url_for('profiles.list_profiles'))
        else:
            print('[ERROR RESPUETA]:', response.status_code, response.text)
            return f"Error al crear perfil: {response.status_code} - {response.text}", 400

    headers = get_auth_headers()
    users_resp = requests.get(f"{current_app.config['API_URL']}/users", headers=headers)
    
    if users_resp.status_code == 401:
        flash('Tu sesión ha expirado, por favor inicia sesión de nuevo.', 'error')
        return redirect(url_for('auth.logout'))

    users = users_resp.json() if users_resp.status_code == 200 else []
    return render_template('profiles/create.html', users=users)

@bp.route('/<int:profile_id>')
@login_required
def view_profile(profile_id):
    headers = get_auth_headers()
    
    # Fetch profile data
    profile_resp = requests.get(f"{current_app.config['API_URL']}/profiles/{profile_id}", headers=headers)
    if profile_resp.status_code != 200:
        flash('Perfil no encontrado.', 'error')
        return redirect(url_for('home.index'))
    
    profile = profile_resp.json()
    
    # Fetch user's posts
    posts_resp = requests.get(f"{current_app.config['API_URL']}/posts/user/{profile['user']['id']}", headers=headers)
    posts = posts_resp.json() if posts_resp.status_code == 200 else []
    
    return render_template('profile/detail.html', profile=profile, posts=posts)

@bp.route('/me')
@login_required
def my_profile():
    headers = get_auth_headers()
    user_id = session['user']['id']
    
    # Obtener el perfil del usuario actual
    profile_resp = requests.get(f"{current_app.config['API_URL']}/profiles/user/{user_id}", headers=headers)
    
    if profile_resp.status_code == 404:
        flash('No tienes un perfil creado. ¡Crea uno ahora!', 'info')
        return redirect(url_for('profiles.create_profile'))
    
    if profile_resp.status_code != 200:
        flash('Error al obtener tu perfil.', 'error')
        return redirect(url_for('home.index'))
        
    profile = profile_resp.json()
    
    # Obtener los posts del usuario
    posts_resp = requests.get(f"{current_app.config['API_URL']}/posts/user/{user_id}", headers=headers)
    posts = posts_resp.json() if posts_resp.status_code == 200 else []
    
    return render_template('profile/detail.html', profile=profile, posts=posts)

@bp.route('/<int:profile_id>/update', methods=['POST'])
@login_required
def update_profile(profile_id):
    headers = get_auth_headers()
    
    form_data = {
        'firstName': request.form.get('firstName'),
        'lastName': request.form.get('lastName'),
    }

    files = {}
    if 'avatar' in request.files and request.files['avatar'].filename != '':
        avatar = request.files['avatar']
        files['avatar'] = (avatar.filename, avatar.stream, avatar.mimetype)

    # Remove content-type from headers for multipart/form-data
    headers.pop('Content-Type', None)

    response = requests.patch(
        f"{current_app.config['API_URL']}/profiles/{profile_id}",
        data=form_data,
        files=files,
        headers=headers
    )

    if response.status_code == 200:
        flash('Perfil actualizado exitosamente.', 'success')
    else:
        flash('Error al actualizar el perfil.', 'error')

    return redirect(url_for('profiles.my_profile'))
