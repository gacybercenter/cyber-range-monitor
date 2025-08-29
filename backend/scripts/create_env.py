
from range_monitor.security import SecurityConnector


def main() -> None:
    secrets = SecurityConnector.temporary_settings().model_dump()
    with open('.env', 'w') as f:
        for key, value in secrets.items():
            f.write(f'{key}="{value}"\n')
    print('Secrets generated and written to .env file')


if __name__ == '__main__':
    main()
