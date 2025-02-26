from .app import AppConfig
from .project import PyProjectInfo


_APP_CONFIG = AppConfig()  # type: ignore
_PROJECT_INFO = PyProjectInfo()  # type: ignore


def running_app_config() -> AppConfig:
    '''Returns the AppConfig instance

    Returns:
        AppConfig: The AppConfig instance
    '''
    return _APP_CONFIG


def running_project() -> PyProjectInfo:
    '''Returns the PyProjectInfo instance

    Returns:
        PyProjectInfo: The PyProjectInfo instance
    '''
    return _PROJECT_INFO



