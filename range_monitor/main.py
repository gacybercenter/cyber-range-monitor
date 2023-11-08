"""
The main module for the Range Monitor application.
"""
import os
# import sys
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
# from werkzeug.exceptions import abort

# from range_monitor.db import get_db
from range_monitor.auth import login_required

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
