from typing import Annotated
from fastapi import Depends
import guacamole
from app.core.errors import HTTPBadRequest

from app.guacamole_source.dependency import GuacControllerDep
from .const import GUAC_CONNECTION


async def get_guacamole_session(
    guac_controller: GuacControllerDep
) -> guacamole.session:
    '''dependency to get the established or new guacamole session
    from the connection class 
    Arguments:
        guac_controller {GuacControllerDep} -- the guacamole controller dependency

    Raises:
        exc: HTTPBadRequest -- if the connection to guacamole fails

    Returns:
        guacamole.session -- the cached or new guacamole session
    '''
    conn = await GUAC_CONNECTION.connect(guac_controller)
    if not conn:
        exc = HTTPBadRequest('Failed to connect to Guacamole')
        exc.label = 'CONNECTION_FAILED'
        raise exc
    return conn


GuacSessionDep = Annotated[guacamole.session, Depends(get_guacamole_session)]
