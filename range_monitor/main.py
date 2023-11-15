"""
The main module for the Range Monitor application.
"""
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from range_monitor.db import get_db
from range_monitor.auth import login_required, user_required, admin_required

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    """
    Route decorator for the index page.

    Returns:
        str: The rendered HTML template for the index page.

    Raises:
        None
    """
    # Get the list of plugin files
    plugins_dir = os.path.join(bp.root_path, 'plugins')
    plugins = os.listdir(plugins_dir)

    return render_template('main/index.html', plugins=plugins)


@bp.route('/users')
@login_required
def users():
    """
    Route decorator for the index page.

    Returns:
        str: The rendered HTML template for the index page.

    Raises:
        None
    """

    db = get_db()
    user_list = db.execute(
        'SELECT p.id, created, username, password, permission'
        ' FROM user p'
        ' ORDER BY p.id'
    ).fetchall()

    return render_template('main/users.html', users=user_list)


@bp.route('/create_user', methods=('GET', 'POST'))
@admin_required
def create_user():
    """
    Creates a new user in the system.

    Parameters:
    - None

    Returns:
    - None
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        permission = request.form['permission']
        error = None

        if not username or not password or not permission:
            error = 'Fill in all required fields.'

        if error is None:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO user (username, password, permission) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), permission),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("main.users"))

        flash(error)

    return render_template('main/create_user.html')


def get_user(identifier):
    """
    Retrieves user information from the database based on the given identifier.

    Parameters:
    - identifier: A unique identifier for the user.

    Returns:
    - user: A dictionary containing the user's information including
        the id, username, password, and permission.

    Raises:
    - 404 Not Found: If the user with the given identifier does not
        exist in the database.
    """
    user = get_db().execute(
        'SELECT p.id, username, password, permission'
        ' FROM user p'
        ' WHERE p.id = ?',
        (identifier,)
    ).fetchone()

    if user is None:
        abort(404, f"User id {identifier} doesn't exist.")

    return user


@bp.route('/<int:identifier>/edit_user', methods=('GET', 'POST'))
@user_required
def edit_user(identifier):
    """
    Renders the edit user page and handles the form submission for updating user information.

    Parameters:
    - identifier (int): The id of the user to edit.

    Returns:
    - redirect: If the form is submitted successfully, redirect to the users page.
    - render_template: If the form is not submitted or there is an error,
        render the edit user template.

    Raises:
    - 403 Forbidden: If the user does not have admin permission and
        the identifier is not the same as the user's id.
    """
    if g.user['permission'] != 'admin' and identifier != g.user['id']:
        abort(403)

    user = get_user(identifier)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        permission = request.form['permission']
        error = None

        if not username or not password or not permission:
            error = 'Fill in all required fields.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET username = ?, password = ?, permission = ?'
                ' WHERE id = ?',
                (username, generate_password_hash(password), permission, identifier)
            )
            db.commit()
            return redirect(url_for('main.users'))

    return render_template('main/edit_user.html', user=user)


@bp.route('/<int:identifier>/delete', methods=('POST',))
@admin_required
def delete(identifier):
    """
    Deletes a user with the given ID from the database.

    Parameters:
        identifier (int): The ID of the user to delete.

    Returns:
        redirect: A redirect response to the main index page.
    """
    get_user(identifier)
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (identifier,))
    db.commit()
    return redirect(url_for('main.users'))



# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO config (title, body, author_id)'
#                 ' VALUES (?, ?, ?)',
#                 (title, body, g.user['id'])
#             )
#             db.commit()
#             return redirect(url_for('main.index'))

#     return render_template('main/create.html')


# def get_config(id, check_author=True):
#     config = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM config p JOIN user u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()

#     if config is None:
#         abort(404, f"Config id {id} doesn't exist.")

#     if check_author and config['author_id'] != g.user['id']:
#         abort(403)

#     return config


# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     config = get_config(id)

#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE config SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('main.index'))

#     return render_template('main/update.html', config=config)


# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_config(id)
#     db = get_db()
#     db.execute('DELETE FROM config WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('main.index'))
