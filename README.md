* Range Monitor v2

The Range Monitor is web-based application that for monitoring and 
interacting, monitoring & browsing Guacamole, OpenStack and Saltstack.

The Range Monitor v2 wil be rewritten in FastAPI for performance, security,
scalability and to expand the existing functionality and scope of the project.
Furthermore, the end goal is creating a more modular and extensible
backend that will serve as the API for a more a robust and modern frontend made in
a Javascript framework. 


 
== Getting Started

* You will first need to have git & pip installed on your
machine

[,git]
----
git clone <http_url>
----

* cd to "src" 

[,bash]
----
cd src
----

=== Create & Activate the virtual environment

*Windows*

[,ps1]
----
py -m venv .venv
.venv\Scripts\activate
----

*Unix Based*

[,bash]
----
python3 -m venv .venv
. .venv/bin/activate
----

*Install the required Python Dependencies*

[,ps1]
----
pip install -r requirements.txt
----

=== Secrets & Environment Setup 

* Change directories to version 2

* Generate the secret keys and required
build settings for the API for both production
and local development by executing the following script

[,bash]
----
py -m scripts.secret_gen
----

**Ouput**

[,bash]
----
/src> py -m scripts.secret_gen
<< ~api\scripts\key_gen.py~ >>
Development environment created
Production secrets created
---

* Confirm the script worked by displaying the database tables in the CLI by
using the following command 

[,bash]
----

version_2> py cli.py show-tables

----

*Optional*

* If you want to save all of the configurations to a .env file for the app 
do the following  

[,bash]
----

version_2> py cli.py export-conf
Build successful
The .env already exists. Do you want to overwrite it? (TYPE "YES"): YES
Exported configuration to .env

----


* Get redis running on your machine using WSL if your on Windows 
and confirm it's running by doing the following 

[,bash]
----
version_2$ redis-cli
127.0.0.1:6379> ping
PONG
----

=== Run the FastAPI application for the first time using the Command Line
[,bash]
----
fastapi dev app
----

== Developer Notes
** *API CLI*: for many of the common tasks you will perform such as reinitializing the database or "peeking" the last 10 items in the database the CLI will be your best friend 
and there is an interactive CLI mode for creating your own custom build configs for the API
  * *CLI Commands*: 
    * *create-db*: initializes the database and creates the tables
    * *show-tables*: displays the tables in the database
    * *peek _model_name*: displays the last 10 items in the table, to see the model names 
    type run the _model-names_ command to see the available models
    * *export-conf*: exports the configuration to a .env file
    * *show-env*: shows the environment variables in the .env file as they are processed by the pydantic base settings class in the application.
    * *conf-help*: shows the documentation for the configuration options 
    * *do-conf*: starts an interactive CLI mode for creating custom build configurations for the API
      * _config-builder_
          ~ To set a field in the build settings for the API type PROP_NAME=VALUE ~ 
          * no-docs - Disables the documentation routes
          * try-build - Tests to see if the configuration is ready to build
          * preview - previews the current configuration, optional prefix to filter configurations (preview <prefix>)
          * export - exports the configuration to a .env file (export )
          * exit - exits the application
          * show-docs - displays the documentation for app settings
          * help - Displays the commands for the CLI
          * clear - Clears the screen of the CLI

** *SwaggerUI API Endpoint Documentation*: one of the best features of FastAPI is the automatic generation of API documentation with SwaggerUI which will detail all of the 
API routes, the expected request & response body and the status codes which 
you can view when you run the application and navigate to the /docs endpoint 
after running the application. *IN PRODUCTION DISABLE THIS FEATURE*

* *VS Code Workspace*: Use the .code-workspace file in the root of the project to open the project in Visual Studio Code with the recommended extensions. This maintains consistency for development and formatting across the project, Click on the .code-workspace file,
and click 'Open Workspace' to open the workspace.

** *Type / Checking IMPORTANT*: the .code-workspace files enforces 'basic' level type checking with pylance for better code readability and to provide a clear definition for an other wise ambigous type. This means you are REQUIRED to provide type hints for functions, variables and it may take some getting used to but it will save you alot of time.   
  ** _Pylance can be a bit overzealous at times and a type error does not mean your code is inherently wrong, such as in instances where a type conversions such as an ORM being serialized implicitly to a Pydantic Model in a response for a route. When this occurs provide *# type: ignore comments to suppress the errors* but it is encouraged to use type hints where possible._

== Resources  

[discrete]
=== Documentation

*FastAPI*: link:https://fastapi.tiangolo.com/learn/[_here_]

*SQLAlchemy Documentation*: link:https://docs.sqlalchemy.org/en/20/intro.html[_here_]

*Pydantic Documentation*: link:https://pydantic-docs.helpmanual.io/[_here_]

=== Recommendations

* *Use a REST Client*: saves you time, effort and offers better security & visibility into API behavior 

- *Insomnia*: A Free REST client that will be invaluable for testing the API endpoints, security and
Pydantic Models (_use hobby version_) which you can install link:https://insomnia.rest/[here]

- *DB Browser for SQLite*: A Free GUI tool for managing SQLite databases which you can install link:https://sqlitebrowser.org/[here]

== Project Structure 

The project structure is designed to be modular to allow shared logic among modules and api routes and follows a "Service" based approach following the Model-View-Controller (MVC) pattern.

* The "*models*" directory contains the database models for the application
    
* The "*middleware*" directory contains all of the request interceptors / middleware for the 
appliacation with the __init__.py file in the package having a "register_middleware" function that registers the middleware with the app instance

* The "*config*" directory contains everything related to the app configuration including the pydantic models and the singleton _AppSettings_ for how the configuration is processed and loaded into the application. Use the "*running_config()*" function to retrieve the running config 

* The "*services*" directory contains all of the services that are used in the routers accross the application and act as the controllers and the core logic of all routers making
the process of implementing working routers simple in most instances.

* The "*routers*" directory contains all of the APIRouters for the application and tend to have minimal logic compared to the service classes.

* The "*common*" directory contains all of the shared logic that is used accross the application such as utilities, constants, and other shared logic.

* The "*schemas*" directory contains all of the Pydantic models for the application and are used for request and response validation in the routers and services.

* The "*security*" directory contains the main auth class based depenedency for the application and the security utilities for the application.
