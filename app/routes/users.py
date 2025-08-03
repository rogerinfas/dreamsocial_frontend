from flask import Blueprint, render_template, request, redirect, url_for, current_app
import requests

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
def list_users():
    resp = requests.get(f"{current_app.config['API_URL']}/users")
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
