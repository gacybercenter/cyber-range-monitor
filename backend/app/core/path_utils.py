from pathlib import Path


def abs_root_path(file: str | Path) -> Path:
    """Takes a file name and relative to the root of the project
    returns it's absolute path.
    """
    if isinstance(file, str):
        file = Path(file)
    path = Path.cwd().joinpath(file)
    return path.resolve()


def get_app_root() -> Path:
    '''
    gets the root path of the application. or the
    `backend` directory.

    Returns
    -------
    Path
    '''
    return Path(__file__).parent.parent.parent.resolve()
