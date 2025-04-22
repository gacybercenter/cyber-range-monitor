EXAMPLE_BASE_REQUEST = {
    'username': 'foo',
    'password': 'bar',
    'endpoint': 'https://example.com',
}

GUAC_REQUEST = {
    **EXAMPLE_BASE_REQUEST,
    'options': {
        'datasource': 'sqlite'
    }
}

SALTSTACK_REQUEST = {
    **EXAMPLE_BASE_REQUEST,
    'options': {
        'hostname': 'saltstack.example.com',
    }
}

OPENSTACK_REQUEST = {
    **EXAMPLE_BASE_REQUEST,
    'options': {
        'project': 'example_project',
        'project_name': 'example_project_name',
        'project_domain': 'example_project_domain',
        'user_domain': 'example_user_domain',
        'region_name': 'example_region_name',
        'identity_api_version': '3',
    }
}

EXAMPLE_BASE_RESPONSE = {
    'id': 1,
    'username': 'foo',
    'enabled': True,
    'endpoint': 'https://example.com',
}

GUAC_RESPONSE = {
    **EXAMPLE_BASE_RESPONSE,
    'options': {
        'datasource': 'sqlite'
    }
}

OPENSTACK_RESPONSE = {
    **EXAMPLE_BASE_RESPONSE,
    'options': {
        'project': 'example_project',
        'project_name': 'example_project_name',
        'project_domain': 'example_project_domain',
        'user_domain': 'example_user_domain',
        'region_name': 'example_region_name',
        'identity_api_version': '3',
    }
}

SALTSTACK_RESPONSE = {
    **EXAMPLE_BASE_RESPONSE,
    'options': {
        'hostname': 'saltstack.example.com',
    }
}
