from flask import Blueprint, render_template, session, abort
import requests

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    return render_template('home.html')

@bp.route('/admin')
def admin_dashboard():
    if not session.get('logged_in') or session['user']['role'] != 'admin':
        abort(403)

    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    
    try:
        users_res = requests.get('http://localhost:3000/users', headers=headers)
        users_res.raise_for_status()
        users_count = len(users_res.json())

        profiles_res = requests.get('http://localhost:3000/profiles', headers=headers)
        profiles_res.raise_for_status()
        profiles_count = len(profiles_res.json())

        posts_res = requests.get('http://localhost:3000/posts', headers=headers)
        posts_res.raise_for_status()
        posts_count = len(posts_res.json())
    except requests.exceptions.RequestException as e:
        return render_template('errors/503.html', error=e)

    return render_template('admin/dashboard.html', users_count=users_count, profiles_count=profiles_count, posts_count=posts_count)
