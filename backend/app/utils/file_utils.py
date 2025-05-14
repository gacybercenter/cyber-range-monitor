from pathlib import Path


def assert_path_exists(file_path: Path) -> None:
    assert file_path.exists(), (
        f"{file_path} does not exist ensure it exists and "
        "your current working directory is correct."
    )


def assert_paths_exist(file_paths: list[Path]) -> None:
    for file_path in file_paths:
        assert_path_exists(file_path)


def abs_root_path(file: str | Path) -> Path:
    """Takes a file name and relative to the root of the project
    returns it's absolute path.

    Arguments:
        file {str | Path} -- the file name to resolve
    Returns:
        Path -- the absolute path to the file
    """
    if isinstance(file, str):
        file = Path(file)
    path = Path.cwd().joinpath(file)
    return path.resolve()
