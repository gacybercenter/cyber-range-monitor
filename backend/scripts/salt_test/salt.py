import pprint
from pathlib import Path

import httpx
from rich.traceback import install as pretty_tb_install

pretty_tb_install(show_locals=True)

async def get_saltstack_token(client: httpx.AsyncClient, credentials: dict) -> str:
    response = await client.post('/login', json={
        'eauth': 'pam',
        **credentials,
    })
    if response.status_code == 401 or response.status_code == 403:
        raise ValueError('Invalid credentials for SaltStack auth')

    response.raise_for_status()
    response_json: dict = response.json()

    pprint.pprint(response_json)
    input('Paused...')
    returned = response_json.get('return')

    if not returned or len(returned) != 1:
        raise ValueError('Invalid response from SaltStack auth endpoint')

    if not (token := returned[0].get('token')):
        raise ValueError('No token found in SaltStack auth response')

    return token


async def run(
    endpoint: str,
    username: str,
    password: str,
):
    client = httpx.AsyncClient(
        base_url=httpx.URL(endpoint, port=8000),
    )
    async with client:
        token = await get_saltstack_token(client, {
            'username': username,
            'password': password,
        })


def read_from_dotenv() -> dict:

    env_contents = Path('.env').read_text().splitlines()
    env_dict = {}
    for line in env_contents:
        name, value = line.split('=')
        env_dict[name] = value
    return env_dict


async def main() -> None:
    kwargs = read_from_dotenv()
    await run(**kwargs)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())