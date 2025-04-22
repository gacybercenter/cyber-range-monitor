# adjust-api - Todo

## General

- [ ] Refactor the "CRUDController" class to be a repository and adjust it so
        services are composed of one instead of inherit to reduce complex class
        inheritance
- [ ] Better naming conventions (e.g BaseModel which is the Base Database Model conflicts with the pydantic base model name so it makes more sense for it be BaseDBModel)
- [ ] Define solid tests for all routes
- [ ] Ensure the openapi schema is compatible and defines all types for the frontend API client (right now PydanticError for ValidationError is not defined in the openapi schema since we have to manually adjust the RequestValidationError response manually)

## Directory Structure Adjustments

-   Create a more intuitive and easier to navigate directory structure, below is the proposed structure:

```

main.py
config/
	(...)
redis/
    (...)
db/
    (...)
	models/
		(...)
    mixins/
        (...)

_router packages (e.g "users") stay the same / flat still except they now no longer
have a models.py_

(...)


core/ (_all of the "base" functionality such as custom base model and base service_)
    errors/
		(...)
        exc_handler.py
	schema/
		(...)
	interfaces/
		(...)
misc/ (_all of the misc functionality such as the logger and the openapi schema_)
    event_logger.py
    api_logger.py
    console.py
    security/
        (...)
    openapi_extra/
        (...)
middleware/
    (...)

```

### Datasources
- [ ] Refactor Datasource router so that it's one route and uses path parameters
- [ ] Refactor each of the schemas to instead of using Inheritance to have a flat
structure and inherit to instead have an "options" property for the extra fields
(e.g)

```python
from typing import Generic, TypeVar
OptionsT = TypeVar('OptionsT', bound=CustomBaseModel)

class DatasourceRead(CustomBaseModel, Generic[OptionsT]):
    id: str
    username: str
    enabled: bool
    endpoint: str
    options: OptionsT
# (e.g)
class GuacamoleOptions(CustomBaseModel)
    datasource
type GuacamoleRead = DatasourceRead[GuacamoleOptions]
```

- [ ] Use an enum path parameter for each of the actions and have the response_model be a Union type of all the possible return types (e.g /datasource/{type}/)
- [ ] Create a DatasourceRepository class for the generalized actions for the datasource that defines all the ORM manipulation
with supported but not required inheritance.
- [ ] Create a DatasourceService with the connect, test_connection, connect_args must implement methods
