from flask import Blueprint, render_template, request, redirect, url_for, current_app
import requests

bp = Blueprint('profiles', __name__, url_prefix='/profiles')

@bp.route('/')
def list_profiles():
    resp = requests.get(f"{current_app.config['API_URL']}/profiles")
    profiles = resp.json() if resp.status_code == 200 else []
    return render_template('profiles/list.html', profiles=profiles)

@bp.route('/create', methods=['GET', 'POST'])
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

        response = requests.post(
            f"{current_app.config['API_URL']}/profiles",
            data=form_data,
            files=files
        )

        if response.status_code == 201:
            return redirect(url_for('profiles.list_profiles'))
        else:
            print('[ERROR RESPUETA]:', response.status_code, response.text)
            return f"Error al crear perfil: {response.status_code} - {response.text}", 400

    users = requests.get(f"{current_app.config['API_URL']}/users").json()
    return render_template('profiles/create.html', users=users)
