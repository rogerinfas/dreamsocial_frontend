from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import requests
from .auth import login_required, get_auth_headers

bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route('/')
@login_required
def list_posts():
    try:
        headers = get_auth_headers()
        response = requests.get(f"{current_app.config['API_URL']}/posts", headers=headers)

        if response.status_code == 401:
            flash('Tu sesión ha expirado, por favor inicia sesión de nuevo.', 'error')
            return redirect(url_for('auth.logout'))

        posts = response.json() if response.status_code == 200 else []
        return render_template('posts/list.html', posts=posts)
    except requests.exceptions.RequestException:
        flash('Error al cargar los posts', 'error')
        return render_template('posts/list.html', posts=[])

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content:
            flash('El contenido del post es requerido', 'error')
            return render_template('posts/create.html')
        
        # Preparar datos del formulario (sin authorId, se obtiene del JWT)
        form_data = {'content': content}
        
        files = {}
        if 'image' in request.files and request.files['image'].filename != '':
            image = request.files['image']
            files['image'] = (image.filename, image.stream, image.mimetype)
        
        try:
            headers = get_auth_headers()
            response = requests.post(
                f"{current_app.config['API_URL']}/posts",
                data=form_data,
                files=files,
                headers=headers
            )
            
            if response.status_code == 201:
                flash('Post creado exitosamente', 'success')
                return redirect(url_for('posts.list_posts'))
            else:
                error_data = response.json()
                flash(error_data.get('message', 'Error al crear el post'), 'error')
        except requests.exceptions.RequestException:
            flash('Error de conexión con el servidor', 'error')
    
    return render_template('posts/create.html')

@bp.route('/<int:post_id>')
@login_required
def view_post(post_id):
    try:
        headers = get_auth_headers()
        response = requests.get(f"{current_app.config['API_URL']}/posts/{post_id}", headers=headers)

        if response.status_code == 401:
            flash('Tu sesión ha expirado, por favor inicia sesión de nuevo.', 'error')
            return redirect(url_for('auth.logout'))

        if response.status_code == 200:
            post = response.json()
            return render_template('posts/detail.html', post=post)
        else:
            flash('Post no encontrado', 'error')
            return redirect(url_for('posts.list_posts'))
    except requests.exceptions.RequestException:
        flash('Error al cargar el post', 'error')
        return redirect(url_for('posts.list_posts'))

@bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    try:
        headers = get_auth_headers()
        response = requests.post(
            f"{current_app.config['API_URL']}/posts/{post_id}/like",
            headers=headers
        )
        
        if response.status_code == 201:
            flash('Post liked!', 'success')
        else:
            flash('Error al dar like', 'error')
    except requests.exceptions.RequestException:
        flash('Error de conexión', 'error')
    
    return redirect(url_for('posts.view_post', post_id=post_id))

@bp.route('/<int:post_id>/unlike', methods=['POST'])
@login_required
def unlike_post(post_id):
    try:
        headers = get_auth_headers()
        response = requests.post(
            f"{current_app.config['API_URL']}/posts/{post_id}/unlike",
            headers=headers
        )
        
        if response.status_code == 201:
            flash('Post unliked!', 'success')
        else:
            flash('Error al quitar like', 'error')
    except requests.exceptions.RequestException:
        flash('Error de conexión', 'error')
    
    return redirect(url_for('posts.view_post', post_id=post_id))

@bp.route('/user/<int:user_id>')
@login_required
def user_posts(user_id):
    try:
        headers = get_auth_headers()
        response = requests.get(f"{current_app.config['API_URL']}/posts/user/{user_id}", headers=headers)

        if response.status_code == 401:
            flash('Tu sesión ha expirado, por favor inicia sesión de nuevo.', 'error')
            return redirect(url_for('auth.logout'))

        posts = response.json() if response.status_code == 200 else []
        
        # Obtener información del usuario
        user_response = requests.get(f"{current_app.config['API_URL']}/users/{user_id}", headers=headers)
        user = user_response.json() if user_response.status_code == 200 else None
        
        return render_template('posts/user_posts.html', posts=posts, user=user)
    except requests.exceptions.RequestException:
        flash('Error al cargar los posts del usuario', 'error')
        return redirect(url_for('posts.list_posts'))

@bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    # Primero obtener el post para verificar que el usuario es el autor
    try:
        headers = get_auth_headers()
        response = requests.get(f"{current_app.config['API_URL']}/posts/{post_id}", headers=headers)

        if response.status_code == 401:
            flash('Tu sesión ha expirado, por favor inicia sesión de nuevo.', 'error')
            return redirect(url_for('auth.logout'))

        if response.status_code != 200:
            flash('Post no encontrado', 'error')
            return redirect(url_for('posts.list_posts'))
        
        post = response.json()
        current_user_id = session.get('user', {}).get('id')
        
        if post['author']['id'] != current_user_id:
            flash('No tienes permisos para editar este post', 'error')
            return redirect(url_for('posts.view_post', post_id=post_id))
        
        if request.method == 'POST':
            content = request.form.get('content')
            
            if not content:
                flash('El contenido del post es requerido', 'error')
                return render_template('posts/edit.html', post=post)
            
            # Preparar datos del formulario
            form_data = {'content': content}
            
            files = {}
            if 'image' in request.files and request.files['image'].filename != '':
                image = request.files['image']
                files['image'] = (image.filename, image.stream, image.mimetype)
            
            try:
                headers = get_auth_headers()
                response = requests.patch(
                    f"{current_app.config['API_URL']}/posts/{post_id}",
                    data=form_data,
                    files=files,
                    headers=headers
                )
                
                if response.status_code == 200:
                    flash('Post actualizado exitosamente', 'success')
                    return redirect(url_for('posts.view_post', post_id=post_id))
                else:
                    error_data = response.json()
                    flash(error_data.get('message', 'Error al actualizar el post'), 'error')
            except requests.exceptions.RequestException:
                flash('Error de conexión con el servidor', 'error')
        
        return render_template('posts/edit.html', post=post)
        
    except requests.exceptions.RequestException:
        flash('Error al cargar el post', 'error')
        return redirect(url_for('posts.list_posts'))

@bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    try:
        headers = get_auth_headers()
        response = requests.delete(
            f"{current_app.config['API_URL']}/posts/{post_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            flash('Post eliminado exitosamente', 'success')
        else:
            error_data = response.json()
            flash(error_data.get('message', 'Error al eliminar el post'), 'error')
    except requests.exceptions.RequestException:
        flash('Error de conexión', 'error')
    
    return redirect(url_for('posts.list_posts'))
