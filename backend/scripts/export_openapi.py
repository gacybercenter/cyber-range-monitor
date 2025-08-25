import json

EXPORT_DESTINATION = '../frontend/openapi.json'


def normalize_path_names(openapi_schema: dict) -> None:
    """Normalizes service names from "userGetAllUsers" to "getAllUsers"

    Taken directly from
        https://fastapi.tiangolo.com/advanced/generate-clients/#preprocess-the-openapi-specification-for-the-client-generator

    Arguments:
        openapi_schema {dict} -- the openapi schema of the app

    Returns:
        dict -- the normalized openapi schema
    """
    path_schema: dict[str, dict] = openapi_schema['paths']

    for path_data in path_schema.values():
        for operation in path_data.values():
            tag = operation['tags'][0]
            operation_id = operation['operationId']
            to_remove = f'{tag}-'
            new_operation_id = operation_id[len(to_remove) :]
            operation['operationId'] = new_operation_id


def main() -> None:
    from monitor_api.main import create_app

    print(f'[*] Exporting openapi.json to frontend @ {EXPORT_DESTINATION}.. [*]')
    openapi_schema = create_app().openapi()
    normalize_path_names(openapi_schema)
    try:
        with open(EXPORT_DESTINATION, 'w') as f:
            schema_str = json.dumps(openapi_schema, indent=2)
            f.write(schema_str)
    except Exception as e:
        print(
            f'(!) Could not export openapi.json to frontend/openapi.json\nDetails: {e}'
        )
        return
    print('\n>> openapi.json exported to frontend - script complete <<\n')


if __name__ == '__main__':
    main()
