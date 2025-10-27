import json
import sys
from pathlib import Path


def normalize_openapi_spec() -> str:
    '''
    Normalizes service names from "userGetAllUsers" to "getAllUsers"

    Taken directly from
    https://fastapi.tiangolo.com/advanced/generate-clients/#preprocess-the-openapi-specification-for-the-client-generator

    Arguments:
        openapi_schema {dict} -- the openapi schema of the app

    Returns:
        dict -- the normalized openapi schema
    '''
    from server.app.main import create_app

    openapi_schema = create_app().openapi()

    path_schema: dict[str, dict] = openapi_schema['paths']

    for path_data in path_schema.values():
        for operation in path_data.values():
            tag = operation['tags'][0]
            operation_id = operation['operationId']
            to_remove = f'{tag}-'
            new_operation_id = operation_id[len(to_remove) :]
            operation['operationId'] = new_operation_id

    return json.dumps(openapi_schema, indent=2)


def main() -> int:
    print("""
*********************
scripts.export_openapi
*********************
Usage: python scripts/export_openapi.py [dest_path | default: ./openapi.json
    """)

    dest_arg = sys.argv[1] if len(sys.argv) > 1 else './openapi.json'

    dest_path = Path(dest_arg)

    print(f'exporting to -> {dest_path}')

    if not dest_path.is_file():
        print('error: The destination path must be a file path ', file=sys.stderr)
        return 1

    print(f'exporting openapi.json to frontend @ {dest_path}.. [*]')

    spec = normalize_openapi_spec()
    try:
        dest_path.write_text(spec)
    except Exception as e:
        print(
            f'error: Failed to write openapi.json to {dest_path}: {e}', file=sys.stderr
        )
        return 1

    print('successfully exported openapi.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
