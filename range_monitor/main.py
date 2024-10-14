"""
The main module for the Range Monitor application.
"""
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    jsonify
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from range_monitor.db import get_db
from range_monitor.auth import login_required, user_required, admin_required

bp = Blueprint('main', __name__)

@bp.before_app_request
def load_plugins():
    """
    This function is a callback registered to run before each request.
    It loads the plugins from the specified directory and stores them
    in the global variable g.plugins.
    """
    plugins_dir = os.path.join('range_monitor', 'plugins')
    plugins = os.listdir(plugins_dir)
    g.plugins = plugins


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
    return render_template('main/index.html')


@admin_required
@bp.route('/sources', methods=['GET'])
def data_sources():
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

    return render_template('main/data_sources.html')

@admin_required
@bp.route('/sources/<string:datasource>/toggle-enabled/<int:entry_id>', methods=['POST'])
def toggle_enabled(datasource, entry_id):
    """
    Toggle the status of an entry in the database.
    
    This function is responsible for toggling the status of an entry in the database.
    """
    refresh = redirect(url_for('main.data_source_entries', datasource=datasource))
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
    db = get_db()

    result = db.execute(
        f"UPDATE {datasource} SET enabled = 0"
    )
    error = None
    if not result:
        error = "Failed to update the status of the entry."
        return jsonify({'success': False, 'error': error}) if is_ajax else refresh
    
    entry = db.execute(
        f"SELECT enabled FROM {datasource} WHERE id = ?",
        (entry_id,)
    ).fetchone()

    if not entry:
        error = f"Entry with id {entry_id} not found."
        return jsonify({'success': False, 'error': error}) if is_ajax else refresh
    
    new_status = not entry['enabled']
    db.execute(
        f"UPDATE {datasource} SET enabled = ? WHERE id = ?",
        (new_status, entry_id)
    )
    db.commit()   
    if is_ajax:
        return jsonify({'success': True, 'message': f'Entry {entry_id} has been toggled.'})
    
    return refresh


        
    


@admin_required
@bp.route('/sources/<string:datasource>', methods=['GET'])
def data_source_entries(datasource):
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
    return render_template('data_sources/data_source_entries.html',
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
            return redirect(url_for('main.data_source_entries', datasource=datasource))

        except db.IntegrityError as e:
            error = e

        if error:
            flash(error)

    # Redirect to the list of data source entries or another appropriate page
    return render_template('data_sources/create_source_entry.html',
                            datasource=datasource,
                            entry=entry)


@admin_required
@bp.route('/sources/<string:datasource>/<int:entry_id>', methods=['GET', 'POST'])
def data_source_entry(datasource, entry_id):
    """
    Updates or deletes a data source entry from the database.

    Args:
        datasource (str): The name of the data source where the entry will be updated.
        entry_id (int): The ID of the entry to update or delete.

    Returns:
        Response: A redirect to the data source listing page.
    """
    db = get_db()
    entry = db.execute(
        f"SELECT * FROM {datasource} WHERE id = ?", (entry_id,)
    ).fetchone()

    if entry is None:
        abort(404, f"Entry id {entry_id} doesn't exist.")

    if request.method == 'POST':
        # Assuming the form data matches the column names in your table.
        # You need to adjust the form field names and the SQL statement accordingly.
        data_to_update = {key: request.form[key] for key in request.form}

        # Construct the SQL statement and parameters
        update_statement = f"UPDATE {datasource} SET "
        update_statement += ", ".join(f"{key} = ?" for key in data_to_update)
        update_statement += " WHERE id = ?"

        parameters = list(data_to_update.values()) + [entry_id]

        # Execute the SQL statement
        db.execute(update_statement, parameters)
        db.commit()  # Don't forget to commit the changes

        return redirect(url_for('main.data_source_entries',
                                datasource=datasource))

    return render_template('data_sources/data_source_entry.html',
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
    return redirect(url_for('main.data_source_entries',
                            datasource=datasource))


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

    return render_template('users/create_user.html')


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

    return render_template('users/edit_user.html', user=user)


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
