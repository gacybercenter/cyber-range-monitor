import requests
import json
from range_monitor.db import get_db

def salt_conn():
    db = get_db()
    salt_entry = db.execute(
        'SELECT s.*'
        ' FROM saltstack s'
        ' WHERE s.enabled = 1'
    ).fetchone()

    if not salt_entry:
        return None
    salt_data = {
        key: salt_entry[key]
        for key in salt_entry.keys()
    }
    return salt_data

def rest_login(username, password, url):
    try:
        login = requests.post(
                    f'https://{url}:8000/login',
                    verify=False,
                    json={
                        'username':username,
                        'password':password,
                        'eauth':'pam'
                    }
                )
        token = json.loads(login.text)["return"][0]["token"]
        if not token: 
            raise ValueError("Authentication failed: no token recieved")
        return token
    except Exception as e:
        print("Unable to authenticate", username, e)
        return False

def execute_function(username, password, url, cmd, args):
    try:
        token = rest_login(username, password, url)
        response = requests.post( 
                    f'https://{url}:8000/',
                    verify=False,
                    headers= {
                        "X-Auth-Token" : token
                    },
                    json = [
                            {
                            'client': 'local',
                            'tgt': 'salt-dev',
                            'fun': cmd,
                            'arg': [args]
                            }
                        ]
                )
        return response.json()
    except Exception as e:
        print("Unable to execute:", e)
        return {'API ERROR': e}
    
def insert_temp_data(hostname, node, sensor, temp, time):
    try: 
      db = get_db()
      db.execute(
          'INSERT INTO salt_temp (hostname, node, sensor, temp, time) VALUES (?, ?, ?, ?, ?)',
          (hostname, node, sensor, temp, time)
      )
      db.commit()
    except Exception as e:
      print("Unable to insert temp data:", e)

def check_db():
    db = get_db()
    rows=db.execute(
        'SELECT * FROM salt_temp'
    ).fetchall()
    result = [dict(row) for row in rows]
    return result