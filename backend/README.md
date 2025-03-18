# Range Monitor v2 (Backend)

The Range Monitor v2 uses FastAPI on the backend and UV to manage dependencies and the pyproject.toml file for specifying and managing project dependencies. Additionally, for Authentication the backend relies on api keys that are managed by Redis and are stateless client side.

## Tools & Technologies

- UV: The package manager for managing dependencies, virtual environments and running scripts for the project such as the CLI.

- FastAPI / uvicorn: FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints and uvicorn is the runtime for the ASGI server.

- Database: The backend uses SQLAlchemy as the Object Relational Mapper (ORM) with SQLite as the underlying database
  used due to it's simplicity.

- Redis: Redis is used to store the API keys and is used to authenticate users to the API to allow for api keys to stateless
  client side and stateful on the server

- API CLI: using UV allows for the CLI to be run with the `uv run` command and the CLI is used to manage the database, manage configs and run the server. For more information on commands and usage view the README.md in CLI directory and for information on the CLI run `uv run api --help`

## Project Structure

### Endpoints

The project follows the reccomended structure of a larger FastAPI application where each service / endpoint of the application is it's own package to prevent circular imports from occuring.

- **model.py**: Contains the SQLAlchemy database model
- **service.py / controller.py**: Contains the business logic for the endpoint
- **schema.py**: defines the Pydantic models for the endpoint and schemas of how data should
  be returned and passed to the API
- **const.py**: Contains the variables that don't change during runtime and typically are static
  / non-dynamic configurations that aren't included the the config.yml file.
- **dependency.py**: Contains the dependencies for the endpoints, by using the dependency injection
  feature of FastAPI, we can inject dependencies into the endpoint functions and have them be resolved
  when a request is sent.
- **router.py**: Contains the FastAPI router for the endpoint and the endpoint functions that are called when a request is sent to the endpoint.

### Core

The core package contains the core functionality of the application such as the database, settings and
the base model in pydantic and other essential functionality

### Extensions

The extensions package contains the extensions that are "extra" to the core functionality of the application such as redis or the api console.

## Configuration

The use of pydantic settings allows for the defination of a config class that automatically loads
data from a file with validation for the data.

There are two config files the application used those being:

- **.env**: contains the application secrets
- **config.yml**: contains the application configuration settings

### config.yml

You will likely almost never change the .env file, however to make testing and running the application
in other environments easier, the config.yml file serves as the configuration file for non-sensitive
settings.

This is incredibly useful for controlling the build steps and for testing the application and the config
can easily be changed via the CLI.

- Each of the "groups" in the config.yml file are loaded into the settings class with most being optional and
  some being required.

- The configs are stored in the configs/ directory with the name `config.<label>.yml` where the label is the label for the config (e.g config.dev.yml -> config_label: dev)

- To change the current config, run the command `uv run api conf set <label>` where the label is the label for the config (e.g dev)

- If your config is invalid, the app will not run and 90% of the errors you get will be due to forgetting to set the proper config.

- For additional highly detailed information about each of the configurations, run "uv run api conf docs" to view the documentation for the config file.

#### "app"

The app group has all of the settings for how the app should build and run

**IMPORTANT**

- **config_label**: refers to the label for the config (e.g config.dev.yml -> config_label: dev)
- **environment**: can either be "local" or "container" which is essential to provide since the
  redis client is connected in different ways depending on the Environment
- **testing**: determines whether or not the application is in testing mode, if it is in testing mode
  some of the configurations are allowed to mutate during runtime and the database is reset on each run
- **env_file**: the path to the .env file, if set to `temp` temporary secrets are created which is how
  the pipeline runs tests.

#### "documentation"

The allowed field determines whether or not the documentation routes should be allowed **DISABLE IN PRODUCTION**

#### "database"

The database group contains the settings for the database connection, ensure the database is setup
such that the url is corresponds to a local directory so that a volume can be mounted to the container

**IMPORTANT**

- **url**: the url for the database connection must start with _sqlite+aiosqlite:///_ or you
  will get an error. Additionally, the url must be a local directory so that a volume can be mounted to the container

- **sqlalchemy_echo**: flag for whether or not SQL statements run under the hood of SQL Alchemy should be printed to the console
  in a production environment, don't enable this as it can expose sensitive information.

#### "redis"

The redis group contains the settings for the redis connection, ensure the redis server is running, DO NOT
INCLUDE THE PASSWORD HERE.

**IMPORTANT**

- **host**: the host for the redis server, if the environment is container, the host should match the hostname of the
  redis container. If the host isn't properly set the API won't build since the redis connection will timeout and the API
  is dependent on the redis connection.

#### "auth"

The auth group contains the settings for the authentication of the API corresponding to the settings for how the
cookie should be assigned, how long the cookie should last client side and additionally the max age for an API Key.

## Auth

The way the API handles authentication is by issuing API Keys to authenticated users which are digitally
signed and correspond to state on the server. Everytime a client requests something from the API and is authorized and if the api key is valid it is extended for another "cookie_exp_hours". None of the state
is stored client side and only the server knows the state of the API Key using Redis to revoke and issue API keys.