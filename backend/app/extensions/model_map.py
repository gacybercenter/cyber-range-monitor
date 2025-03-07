



def get_model_map() -> dict:
    '''returns a dictionary of all the models for the CLI to inspect

    Returns:
        dict -- the model map
    '''
    from app.users.model import User
    from app.logging.model import EventLog
    from app.datasources.model import Guacamole, Openstack, Saltstack
    
    return {
        'users': User,
        'event_logs': EventLog,
        'guacamole': Guacamole,
        'openstack': Openstack,
        'saltstack': Saltstack
    }