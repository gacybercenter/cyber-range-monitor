# Range Monitor v2

## Table of Contents

The Range Monitor is a web-based application for monitoring and 
interacting with Guacamole, OpenStack, and Saltstack datasources inside of the 
Georgia Cyber Range.

The Range Monitor v2 relies on FastAPI on the backend with improved API Security, performance and
better seperation of concern. The frontend will be built in Sveltekit + Vite + NodeJS on the frontend,
to support the increasing UI reactivity requirements and to make use of a TypeScript generated API client
provided from the OpenAPI documentation via FastAPI.

## Getting Started (Backend)

**Prerequisites**
* Git and UV installed on your machine
* You can install UV by following the tutorial at [UV Install & Setup](https://docs.astral.sh/uv/#highlights)
* Redis on a Unix System or on Windows via WSL.

### Initial Setup

* Clone the repository

```git
git clone <repo>
```

* Navigate to the backend directory and sync the lock file to create the virtual environment 

```bash
cd backend
uv sync 
```

### Setup Environment, Secrets & Database

* Activate the virtual environment created by UV

```powershell
.venv\Scripts\activate
```

* Generate the secret keys for the API

```bash
py -m scripts.create_env
```

**Output**

```bash
/backend> py -m scripts.create_env
Writing secrets to .env file in backend...
Copying secrets to project root...
 script complete and secrets written to .env
```

* Create the database with the seed data using the API CLI 

```powershell
uv run api db create
```

* Set the current _config.yml_ file to "dev" (configs\config.dev.yml) by running:

```powershell
uv run api conf set dev
```

### Redis Setup

**Note**: The API requires Redis which is only available on Unix-based operating systems.
On Windows, you can use Windows Subsystem for Linux (WSL) or a Docker container.

* [WSL Install Tutorial](https://medium.com/@liu-qilong/a-complete-guide-to-setup-wsl-windows-subsystem-for-linux-4547e88b6cdb)

* Install Redis in WSL or on your device:

```bash
sudo apt-get install redis-server
# Start the Redis server
sudo service redis-server start
# Confirm the Redis Server is running in the Redis CLI 
redis-cli
ping 
exit
# Output to ping should be PONG
```

**Output**
```bash
rhawk@RTop:cyber-range-monitor-v-2/backend$ redis-cli
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> exit
```

### Run the API 

With Redis, the Database, and secrets created, you can run the API. If you did not install Redis on your machine, follow the Docker instructions.

Before starting, ensure:
- Your virtual environment is activated
- Your config.yml file matches your desired environment
- A _".env"_ file exists in both the project root and the _"backend"_ directory

#### Local

* Set the current config to "dev" in the backend directory:

```bash
uv run api conf set dev
```

**Output**
```powershell
backend> uv run api conf set dev
 << ~ (range_monitor_api)$config-yml-setter >> 
 ** INFO **  | Exporting dev to config.yml
 ** INFO **  | Export complete.
```

* Run the API via the CLI:

```bash
uv run api start dev
```

**Output**

```bash
cyber-range-monitor-v-2\backend> uv run api start dev
 ** INFO **  | Starting running API in Dev mode...

   ** FastAPI **   Starting development server 🚀
 
        Searching for package file structure from directories with __init__.py files
```

* _To stop the API, press _"Ctrl + C"_ in the terminal_

_Developer Note_: When you use "api start <mode>", the "mode" section in config.yml 
determines whether the API runs in "dev" or "run" mode. Dev mode in FastAPI 
automatically reloads the server when changes are made to the code
and runs the server on localhost. Production mode does not reload when changes occur,
and the port is exposed on your system.

#### Run via Docker 

* Navigate to the backend directory and set the config.yml file to the "docker" config:

```bash
cd backend
uv run api conf set docker
```

**Output**

```powershell
cyber-range-monitor-v-2\backend> uv run api conf set docker
 << ~ (range_monitor_api)$config-yml-setter >> 
 ** INFO **  | Exporting docker to config.yml
 ** INFO **  | Export complete.
```

* Navigate to the project root and build the Docker container for Redis and the API, 
and ensure that the .env file created earlier is present in the project root.

```bash
cd ..
docker compose up --build
```

* The docker container should now be running, and you can access the API at localhost:8000

## Getting Started, Frontend (WORK IN PROGRESS)


**Prerequisites**

* [NodeJS](https://nodejs.org/en)



### Initial Setup

* Navigate to the frontend directory and install the dependencies

```bash
cd frontend
npm install
```


## Developer Notes

* **Additional Documentation**: For additional context, view the README files for both the frontend and backend directories.

* **OpenAPI**: FastAPI automatically generates an OpenAPI schema for the API, detailing all routes, request/response bodies, and status codes which can be viewed at the `/docs` endpoint where you can test
routes, view response & body schemas and the doc strings for each of the routes. **Note**: In production, disable this feature for security.

* **VS Code Workspace**: Use the .code-workspace file in the project root to better focus on either the frontend or backend and
use the reccomended extensions for better development experience and code consistency / quality.

* **Type Checking**: The workspace enforces 'basic' level type checking with Pylance for better code readability
and clear type definitions. You are required to provide type hints for functions and variables.
For type conversion cases where Pylance flags errors, use `# type: ignore` to suppress them.

## Resources  

### Documentation

* **FastAPI**: [Documentation](https://fastapi.tiangolo.com/learn/)

* **SQLAlchemy**: [Documentation](https://docs.sqlalchemy.org/en/20/intro.html)

* **Pydantic**: [Documentation](https://pydantic-docs.helpmanual.io/)

### Recommendations

* **REST Client**: Use a dedicated client for testing the API:
  * **Insomnia**: A free REST client valuable for testing API endpoints, security, and
    Pydantic Models (use hobby version). Available at [Insomnia.rest](https://insomnia.rest/)

* **DB Browser for SQLite**: A free GUI tool for managing SQLite databases.
  Available at [SQLiteBrowser.org](https://sqlitebrowser.org/)