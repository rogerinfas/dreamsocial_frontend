from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
import requests
from .auth import get_auth_headers, login_required

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
@login_required
def list_users():
    headers = get_auth_headers()
    resp = requests.get(f"{current_app.config['API_URL']}/users", headers=headers)
    
    if resp.status_code == 401:
        flash('Tu sesión ha expirado, por favor inicia sesión de nuevo.', 'error')
        return redirect(url_for('auth.logout'))
        
    users = resp.json() if resp.status_code == 200 else []
    return render_template('users/list.html', users=users)

@bp.route('/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        payload = { 'email': email, 'password': password }
        requests.post(f"{current_app.config['API_URL']}/users", json=payload)
        return redirect(url_for('users.list_users'))
    return render_template('users/create.html')
