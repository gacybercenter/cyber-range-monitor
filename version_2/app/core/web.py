from pathlib import Path
from typing import Optional

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


WEB_ROOT = Path().cwd().absolute() / 'frontend'


def verify_web_context(base_dir: str, sub_dir: Optional[str] = None) -> str:
    base_path = WEB_ROOT / base_dir
    if not base_path.exists():
        raise FileNotFoundError(f'Web path {base_path.name} does not exist')

    if not sub_dir:
        return str(base_path)

    sub_path = base_path / sub_dir
    if not sub_path.exists():
        raise FileNotFoundError(f'Web path {sub_path.name} does not exist')

    return str(sub_path)


def create_static(sub_dir: Optional[str] = None) -> StaticFiles:
    return StaticFiles(
        directory=verify_web_context('static', sub_dir)
    )


def create_template(sub_dir: Optional[str] = None) -> Jinja2Templates:
    return Jinja2Templates(
        directory=verify_web_context('pages', sub_dir)
    )


main_template = create_template()
main_static = create_static()


def main() -> None:
    print(WEB_ROOT)


if __name__ == '__main__':
    main()
