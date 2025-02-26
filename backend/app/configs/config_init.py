import os
from pydantic_settings import SettingsConfigDict

shown_warning = False


def settings_config(env_prefix: str) -> SettingsConfigDict:
    '''gets the right env_file for the pydantic settings
    Arguments:
        env_prefix {str} -- an optional env prefix

    Returns:
        SettingsConfigDict
    '''
    app_env = os.getenv('APP_ENV', 'not-set')
    global shown_warning
    if app_env == 'not-set':
        if not shown_warning:
            print('WARNING: APP_ENV is not set, setting environment to dev')
            shown_warning = True
        env_file = 'dev.env'

    env_file = 'prod.env'
    if app_env == 'dev':
        env_file = 'dev.env'
        
    return SettingsConfigDict(
        env_prefix=env_prefix,
        env_file=env_file,
        env_file_encoding='utf-8',
        extra='ignore',
    )
