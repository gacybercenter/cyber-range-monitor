"""
Handles authentication for the application.
"""
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from range_monitor.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    Register a new user.

    This function handles the registration process for a new user. It is a route
    function that is triggered when a user accesses the '/register' endpoint
    with either a GET or POST request. If the request method is POST, the
    function retrieves the username and password from the request form, checks
    if the required fields are filled, and then inserts the user into the
    database. If the insertion is successful, the user is redirected to the
    login page. If there are any errors during the registration process, an
    error message is flashed to the user.

    Parameters:
    - None

    Returns:
    - None
    """

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, permission) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), 'user'),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    Login route handler.

    Handles the login functionality for the '/login' route. This function is
    triggered when a GET or POST request is made to '/login'. If the request
    method is POST, it retrieves the username and password from the request
    form, checks if the user exists in the database, and verifies the password.
    If the login is successful, it clears the session and sets the 'user_id'
    key in the session to the user's ID. It then redirects the user to the
    'index' route. If the login is unsuccessful, it flashes an error message.

    Returns:
        If the request method is POST and the login is successful, it redirects
        the user to the 'index' route. Otherwise, it renders the 'login.html'
        template.
    """

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """
    Load the logged in user before every application request.

    This function retrieves the user ID from the session and checks if it exists.
    If the user ID is not found, the `g.user` attribute is set to `None`.
    Otherwise, the user details are retrieved from the database using the `get_db` function,
    and the user details are stored in the `g.user` attribute.

    Parameters:
        None

    Returns:
        None
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """
    Logs out the current user by clearing the session.

    Returns:
        A redirect response to the index page.
    """
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """
    Decorator that checks if the user is logged in before executing
    the view function.

    Parameters:
    - view: The view function to be wrapped.

    Returns:
    - The wrapped view function.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """
        Decorator that wraps a view function, checking if the user
        is authenticated. If the user is not authenticated, it redirects
        them to the login page.
        
        Parameters:
            **kwargs (dict): Keyword arguments passed to the view function.
        
        Returns:
            The result of the view function.
        """
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def user_required(view):
    """
    Decorator that checks if the user has the required permission to
    access a view.
    
    Args:
        view: The view function to be wrapped.
    
    Returns:
        The wrapped view function.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """
        A function that wraps another function and checks if the user has
        the required permission before executing the wrapped function.

        Parameters:
            kwargs (dict): A dictionary of keyword arguments to be passed
            to the wrapped function.

        Returns:
            Any: The return value of the wrapped function.
        """
        if g.user is None:
            return redirect(url_for('auth.login'))

        if g.user['permission'] not in ['user', 'admin']:
            flash("Access denied. Admin or user permission required.", 'error')
            return redirect(request.referrer or url_for('index'))

        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    """
    Decorator that checks if the user has admin permission before
    executing the view.

    Parameters:
    - view: The view function to be decorated.

    Returns:
    - wrapped_view: The decorated view function.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """
        Executes the wrapped view function if the user has the
        'admin' permission.

        Parameters:
            kwargs (dict): A dictionary of keyword arguments
            passed to the view function.

        Returns:
            str: If the user does not have the 'admin' permission,
            returns an error message. Otherwise, returns the result
            of executing the view function.
        """
        if g.user is None:
            return redirect(url_for('auth.login'))

        if g.user['permission'] not in ['admin']:
            flash("Access denied. Admin permission required.", 'error')
            return redirect(request.referrer or url_for('index'))

        return view(**kwargs)

    return wrapped_view
