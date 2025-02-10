import subprocess
import platform
import secrets
from cryptography.fernet import Fernet


def copy_to_clipboard(text) -> bool:
    system = platform.system().lower()
    if system == 'darwin':
        cmd = ['pbcopy']
    elif system == 'windows':
        cmd = ['clip']
    else:
        cmd = ['xclip', '-selection', 'clipboard']

    try:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
        return True
    except:
        return False


def main(copy_str: bool = True) -> str:
    SECRET_KEY = secrets.token_urlsafe(32)
    SIGNATURE_SALT = secrets.token_urlsafe(32)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    CSRF_SECRET_KEY = secrets.token_urlsafe(32)
    DATABASE_URL = 'sqlite+aiosqlite:///instance/app.db'
    str_secrets = f'''
SECRET_KEY={SECRET_KEY}
SIGNATURE_SALT={SIGNATURE_SALT}
ENCRYPTION_KEY={ENCRYPTION_KEY}
CSRF_SECRET_KEY={CSRF_SECRET_KEY}
DATABASE_URL={DATABASE_URL}
'''
    if copy_str:
        copy_to_clipboard(str_secrets)
    input('>> Application Secret Keys and required fields are copied and ready to paste in .env file.')

    return str_secrets
    

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
