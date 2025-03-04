from fastapi.testclient import TestClient

from app.build import create_app

client = TestClient(create_app())

def test_credentials() -> None:
    response = client.post(
        '/auth/login',
        data={'username': 'admin', 'password': 'admin'}
    )
    assert response.status_code == 200, 'Login failed for credentials that should work (admin, admin)'
    response = client.post(
        '/auth/login',
        data={'username': 'invalid', 'password': 'invalid'}
    )
    assert response.status_code == 401, 'Login succeeded for credentials (invalid, invalid)'
    

def test_revoked_session() -> None:
    response = client.post(
        '/auth/login',
        data={'username': 'admin', 'password': 'admin'}
    )
    session_id = response.cookies['session_id']
    response = client.post(
        '/auth/logout',
        cookies={ 'session_id': session_id }
    )
    
    response = client.get('/logs/today/', cookies={ 'session_id': session_id })
    assert response.status_code == 401, 'Session was not revoked'
    

def test_rbac() -> None:
    response = client.post(
        '/auth/login',
        data={ 'username': 'guest', 'password': 'guest' }
    )
    session_id = response.cookies['session_id']
    
    read_res = client.get('/user/read/1/', cookies={ 'session_id': session_id })
    assert read_res.status_code == 403, 'read only user was able to read user data'
    read_all_res = client.get('/user/all/', cookies={ 'session_id': session_id })
    assert len(read_all_res.json()) == 1, 'read only user was able to users with higher permissions'


    
    
    


