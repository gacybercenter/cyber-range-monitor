

def get_model_map() -> dict:
    '''returns a dictionary of all the models for the CLI to 
    interface with

    Returns:
        dict -- the model map
    '''
    from db.models.user import User
    from db.models.event_log import EventLog

    from app.datasource.guacamole_source.model import GuacamoleSource
    from app.datasource.openstack_source.model import OpenstackSource
    from app.datasource.saltstack_source.model import SaltstackSource

    return {
        'users': User,
        'event_logs': EventLog,
        'guacamole': GuacamoleSource,
        'openstack': OpenstackSource,
        'saltstack': SaltstackSource
    }
