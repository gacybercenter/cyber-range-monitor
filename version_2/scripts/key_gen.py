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


def url_safe() -> str:
    key_len = random.randint(32, 40)
    secret_key = secrets.token_urlsafe(key_len)
    return secret_key


def fernet_enc_key() -> str:
    return Fernet.generate_key().decode()


def token_hex() -> str:
    return secrets.token_hex(32)


def main() -> None:

    console_hdr = '''
      (?) range_monitor_secrets (?)
        | Secret Key Generator |
    _____________________________________
            
            
    1. Fernet Secret Key
    2. URL Safe Secret Key
    3. Token Hex Key
    
    Type anything else to exit the program.
        
    _____________________________________
    >>'''

    choice = ''
    OPTIONS = ['1', '2', '3']
    while True:
        choice = input(console_hdr)
        if not choice in OPTIONS:
            break
        key = None
        if choice == '1':
            key = fernet_enc_key()
        elif choice == '2':
            key = url_safe()
        elif choice == '3':
            key = token_hex()
        if key:
            copy_to_clipboard(key)
            input('>> Key Copied to Clipboard Press [ENTER] to continue...')


if __name__ == '__main__':
    main()
