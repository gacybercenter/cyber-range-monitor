from range_monitor import create_app


def test_config():
    """
    Test the configuration of the application.

    This function asserts that the application created by the `create_app` function
    does not have the `testing` attribute set to `True`. It also asserts that when
    the `create_app` function is called with the `TESTING` parameter set to `True`,
    the `testing` attribute of the created application is set to `True`.

    Args:
        None

    Returns:
        None
    """
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    """
    Generates a function comment for the given function body.
    
    Args:
        client: The client object used to make HTTP requests.
        
    Returns:
        None
    """
    response = client.get('/hello')
    assert response.data == b'Hello, World!'