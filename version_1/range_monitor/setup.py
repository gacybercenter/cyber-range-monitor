from flask import Flask, send_from_directory, abort, flash
from importlib import import_module
import os


def import_plugins(app: Flask):
    '''
    Imports and registers the blueprints for the plugins 
    in the 'plugins' directory (as of now: guacamole, openstack,
    saltstack).

    Parameters:
    - app (Flask): The Flask application object.
    Returns:
    - None
    '''
    print("=" * os.get_terminal_size().columns)
    print("[*] Plugins [*] ")
    plugins_path = os.path.join(app.root_path, 'plugins')
    for plugin in os.listdir(plugins_path):
        plugin_module = import_module(f'range_monitor.plugins.{plugin}')
        bp = getattr(plugin_module, 'bp')
        app.register_blueprint(bp, url_prefix=f"/{plugin}")
        print(f"[*] Loaded plugin '{plugin}'")
    print("=" * os.get_terminal_size().columns)

def share_components(app: Flask):
    @app.route('/shared/components/<path:filename>')
    def share_comps_route(filename):
        """
        Route to serve shared components (i.e css and js files in root 
        static).

        Parameters:
        - filename (str): The name of the file to serve in 
        the 'static/css' or 'static/js/components.

        Returns:
        - response (Response): The response object.
        """
        if not filename.endswith(('.css', '.js')):
            abort(404)
        try:
            file_ext = filename.split('.')[-1]
            resrc_path = os.path.join(
                app.root_path, app.static_folder, file_ext, 'components'
            )
            print(f"debug info {file_ext} | {app.static_folder} | {resrc_path}")
            return send_from_directory(resrc_path, filename)
        except IndexError:
            flash(f"[-] ComponentsError: Bad Filename'{filename}'")
            abort(404)
        except FileNotFoundError:
            flash(f"[-] ComponentsError: '{filename}' not found", 'error')
            abort(404)
