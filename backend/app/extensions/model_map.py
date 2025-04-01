

def get_model_map() -> dict:
    '''returns a dictionary of all the models for the CLI to inspect

    Returns:
        dict -- the model map
    '''
    from app.users.model import User
    from app.event_logs.model import EventLog

    from app.guacamole_source.model import GuacamoleSource
    from app.openstack_source.model import OpenstackSource
    from app.saltstack_source.model import SaltstackSource

    return {
        'users': User,
        'event_logs': EventLog,
        'guacamole': GuacamoleSource,
        'openstack': OpenstackSource,
        'saltstack': SaltstackSource
    }
