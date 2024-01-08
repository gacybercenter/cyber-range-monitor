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


@admin_required
@bp.route('/sources', methods=['GET'])
def list_data_sources():
    """
    List all the data sources.

    This function is responsible for listing all the data sources available in the system.
    It is decorated with the `@admin_required` decorator, which ensures that only users with
    administrative privileges can access this route.

    Parameters:
        None

    Returns:
        str: The rendered HTML template containing the list of data sources.
    """
    plugins_dir = os.path.join(bp.root_path, 'plugins')
    plugins = os.listdir(plugins_dir)
    return render_template('datasources/list_data_sources.html',
                           plugins=plugins)


@admin_required
@bp.route('/sources/<string:datasource>', methods=['GET'])
def list_data_source_entries(datasource):
    """
    Retrieve a list of entries from the specified data source.

    Parameters:
        datasource (str): The name of the data source.

    Returns:
        str: The rendered HTML template containing the list of entries.
    """
    db = get_db()
    entries = db.execute(
        f"SELECT p.* FROM {datasource} p ORDER BY p.id"
    ).fetchall()
    return render_template('datasources/list_data_source_entries.html',
                           entries=entries,
                           datasource=datasource)


@bp.route('/create_source_entry/<string:datasource>', methods=('GET', 'POST'))
@admin_required
def create_source_entry(datasource):
    """
    Creates a new data source entry in the database.

    Args:
        datasource (str): The name of the data source where the entry will be created.

    Returns:
        Response: A redirect to the data source listing page.
    """
    db = get_db()
    entry = db.execute(
        f'SELECT * FROM {datasource} ORDER BY id'
    ).fetchone()

    entry = entry.keys()
    entry.remove('id')

    error = None
    # Extract plugin-specific data from the form
    entry_data = dict(request.form)
    if entry_data:
        values = tuple(entry_data.values())
        try:
            # Retrieve data from form or API to create a new entry
            # Example: data = request.form['data']

            columns = ', '.join(entry_data.keys())
            placeholders = ', '.join('?' for _ in values)
            db.execute(
                f"INSERT INTO {datasource} ({columns}) VALUES ({placeholders})",
                values
            )

            db.commit()
            return redirect(url_for('main.list_data_source_entries', datasource=datasource))

        except db.IntegrityError:
            error = "Data source entry creation failed."

        if error:
            flash(error)

    # Redirect to the list of data source entries or another appropriate page
    return render_template('datasources/create_source_entry.html',
                            datasource=datasource,
                            entry=entry)


@admin_required
@bp.route('/sources/<string:datasource>/<int:entry_id>', methods=['GET', 'POST'])
def data_source_entry(datasource, entry_id):
    """
    Retrieves a specific entry from a given data source.

    Parameters:
        datasource (str): The name of the data source.
        entry_id (int): The ID of the entry to retrieve.

    Returns:
        str: The rendered template for displaying the data source entry.
    """
    db = get_db()
    entry = db.execute(
        f"SELECT * FROM {datasource} WHERE id = ?", (entry_id,)
    ).fetchone()

    if request.method == 'POST':
        # Handle POST request to update the entry
        pass

    return render_template('datasources/data_source_entry.html',
                           entry=entry,
                           datasource=datasource)


@bp.route('/delete_source_entry/<string:datasource>/<int:entry_id>', methods=['POST'])
@admin_required
def delete_source_entry(datasource, entry_id):
    """
    Deletes a data source entry from the database.

    Args:
        entry_id (int): The ID of the entry to delete.

    Returns:
        Response: A redirect to the data source listing page.
    """
    db = get_db()
    error = None

    try:
        # Delete the entry with the given entry_id
        db.execute(f"DELETE FROM {datasource} WHERE id = ?", (entry_id,))
        db.commit()

    except db.IntegrityError:
        error = "Data source insertion failed."

    if error:
        flash(error)

    # Redirect to the list of data source entries or another appropriate page
    return redirect(url_for('main.list_data_source_entries',
                            datasource=datasource))


# @bp.route('/data_sources', methods=('GET', 'POST'))
# @admin_required
# def data_sources():
#     """
#     Adds data sources to the database
    
#     Parameters:
#     - None

#     Returns:
#     - None
#     """
#     plugins_dir = os.path.join(bp.root_path, 'plugins')
#     plugins = os.listdir(plugins_dir)

#     db = get_db()
#     datasources = {
#         plugin: db.execute(
#             'SELECT p.*'
#             f' FROM {plugin} p'
#             ' ORDER BY p.id'
#         ).fetchall()
#         for plugin in plugins
#     }

#     if request.method == 'POST':
#         try:
#             db = get_db()
#             for plugin in plugins:
#                 # Extract plugin-specific data from the form
#                 plugin_data = {
#                     key.replace(f"{plugin}-", ""):
#                         value for
#                         key, value in request.form.items()
#                         if key.startswith(f"{plugin}-")
#                 }
#                 print (plugin_data)
#                 if plugin_data:
#                     identifier = plugin_data.pop('id', None)
#                     assignments = ', '.join(
#                         f"{column} = ?"
#                         for column in plugin_data.keys()
#                     )
#                     values = tuple(plugin_data.values())
#                     if identifier in datasources[plugin]:
#                         # Perform an update if 'id' was provided
#                         db.execute(
#                             f"UPDATE {plugin} SET {assignments} WHERE id = ?",
#                             values + (identifier,)
#                         )
#                     else:
#                         # Perform an insert if no 'id' was provided
#                         columns = ', '.join(plugin_data.keys())
#                         placeholders = ', '.join('?' for _ in values)
#                         db.execute(
#                             f"INSERT INTO {plugin} ({columns}) VALUES ({placeholders})",
#                             values
#                         )
#             db.commit()
#             # Redirect or handle after successful update/insert
#             return redirect(url_for("main.data_sources"))
#         except db.IntegrityError as e:
#             error = f"A DB integrity error occurred. '{e}'"
#             flash(error)

#     return render_template('main/data_sources.html',
#                            datasources=datasources)



# @bp.route('/data_source/<plugin>', methods=['GET', 'POST'])
# @admin_required
# def data_source(plugin):
#     """
#     Renders the active connections from the server or handles the POST request to insert data.

#     Returns:
#         str: The rendered HTML template for displaying the active connections or error messages.
#     """
#     if request.method == 'POST':
#         datasource = request.form['datasource']
#         error = None

#         try:
#             db = get_db()
#             db.execute(
#                 "INSERT INTO data_sources (values) VALUES (?)",
#                 (datasource,),
#             )
#             db.commit()
#         except db.IntegrityError:
#             error = "Data source insertion failed."

#         if error:
#             flash(error)

#     return render_template('main/data_source.html')


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

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        permission = request.form['permission']
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


@bp.route('/edit_user/<int:identifier>', methods=('GET', 'POST'))
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
        permission = request.form.get('permission', user['permission'])
        error = None

        if not username or not password:
            error = 'Fill in all required fields.'

        if error:
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


@bp.route('/delete_user/<int:identifier>', methods=('POST',))
@admin_required
def delete_user(identifier):
    """
    Deletes a user with the given ID from the database.

    Parameters:
        identifier (int): The ID of the user to delete.

    Returns:
        redirect: A redirect response to the main index page.
    """
    if identifier == g.user['id']:
        abort(403)

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
