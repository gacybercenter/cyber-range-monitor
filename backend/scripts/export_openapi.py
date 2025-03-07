import json
import os 
import subprocess

def main() -> None:
    from app.build import create_app
    with open("../frontend/openapi.json", "w") as f:
        f.write(json.dumps(create_app().openapi(), indent=2))
    print('\n>> openapi.json exported <<\n')
    os.chdir('../frontend')
    subprocess.run(['npm', 'run', 'create-client'])

if __name__ == "__main__":
    main()