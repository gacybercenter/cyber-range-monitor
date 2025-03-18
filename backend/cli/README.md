# CLI Command Reference

The API CLI provides several namespaces for managing configurations, inspecting the database, 
and running the application. To get more information on how to use each command,
run `uv run api <namespace> --help`.

## Main CLI Structure

The API CLI is organized into three primary namespaces:

* `start` - Commands for running the application
* `conf` - Commands for managing application configuration
* `db` - Commands for database operations

To view help information for any command, add `--help` to the command:

```bash
uv run api --help
uv run api start --help
uv run api conf --help
uv run api db --help
```

## Start Commands

The `start` namespace provides commands for running the application in different environments.

```bash
uv run api start --help
```

### `dev`

Runs the API in development mode with automatic reloading on code changes.

```bash
uv run api start dev
```

This command:
- Starts the FastAPI development server
- Enables automatic reloading when code changes are detected
- Runs the server on localhost

### `prod`

Runs the API in production mode with no automatic reloading.

```bash
uv run api start prod
```

### `container`

Runs the API in a container environment, automatically detecting the appropriate mode from the config.yml file.

```bash
uv run api start container
```

This command:
- Reads the config.yml file to determine the environment label
- Uses development mode if the label is not 'prod'
- Sets the port to 8000 and host to 0.0.0.0
- Enables reloading regardless of environment

## Configuration Commands

The `conf` namespace provides commands for managing application configuration.

```bash
uv run api conf --help
```

### `docs`

Displays documentation for the config.yml file structure, optionally filtered by a specific group.

```bash
uv run api conf docs
uv run api conf docs auth
```


### `set`

Sets the current configuration by exporting the contents of a a configs.label.yml file to the 
config.yml in the backend directory

```bash
uv run api conf set dev
```

### `show`

Displays the current configuration loaded from config.yml with the types of each of the values and
whether or not the config is required or not

```bash
uv run api conf show
```

### `groups`

Displays the names of all configuration groups/sections in the YML file and the name in the CLI

```bash
uv run api conf groups
```

This command lists all configuration group names available for reference with other commands.

## Database Commands

The `db` namespace provides commands for database operations.

```bash
uv run api db --help
```

### `create`

Creates the database and seeds it.

```bash
uv run api db create
```

#### `reset`

Reinitializes the database by dropping all tables and reseeds it with the seed.

```bash
uv run api db reset
```


### `names`

Shows the CLI names of the database tables for reference in other commands.

```bash
uv run api db names
```

### `show`

Shows the contents of a specific database table, displaying up to 10 rows.

```bash
uv run api db show <model_name>
```


### `tables`

Shows information about all tables in the database, including the names, schema, CLI Name and Table Size

```bash
uv run api db tables
```
