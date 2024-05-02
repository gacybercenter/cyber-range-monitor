"""
Flask app for Cyber Range Monitor
"""

import os
from importlib import import_module
from flask import Flask

def create_app(test_config=None):
    """
    Create and configure the Flask application.

    Parameters:
    - test_config (dict, optional): A dictionary containing the test configuration.
    Defaults to None.

    Returns:
    - app (Flask): The Flask application object.
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'range_monitor.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        """
        This function handles the '/hello' route.
        It is a GET request handler that returns the string 'Hello, World!'.
        """
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='index')

    plugins_dir = os.path.join('range_monitor', 'plugins')
    plugins = os.listdir(plugins_dir)

    for plugin in plugins:
        if plugin == "openstack":
            continue
        plugin_module = import_module(f'range_monitor.plugins.{plugin}')
        bp = getattr(plugin_module, 'bp')
        app.register_blueprint(bp, url_prefix=f"/{plugin}")
        print(f" * Loaded plugin '{plugin}'")

    return app
