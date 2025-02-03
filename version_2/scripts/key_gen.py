import random
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


def main() -> None:
    SECRET_KEY = secrets.token_urlsafe(32)
    SIGNATURE_SALT = secrets.token_urlsafe(32)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    CSRF_SECRET_KEY = secrets.token_urlsafe(32)

    str_secrets = f'''
SECRET_KEY={SECRET_KEY}
SIGNATURE_SALT={SIGNATURE_SALT}
ENCRYPTION_KEY={ENCRYPTION_KEY}
CSRF_SECRET_KEY={CSRF_SECRET_KEY}
'''
    copy_to_clipboard(str_secrets)
    input('>> Application Secret Keys copied and ready to paste in .env file.')

if __name__ == '__main__':
    main()
    input('>> Key Copied to Clipboard Press [ENTER] to continue...')


if __name__ == '__main__':
    main()
