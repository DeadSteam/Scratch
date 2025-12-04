# Service Layer Documentation

## Overview
Business logic layer with validation, error handling, and transaction management.

## Architecture

```
Controllers (API) → Services → Repositories → Database
                      ↓
                  Exceptions
```

## Service Responsibilities

1. **Business Logic**: Enforce business rules and constraints
2. **Validation**: Validate data beyond schema validation
3. **Orchestration**: Coordinate multiple repositories
4. **Error Handling**: Convert repository errors to service exceptions
5. **Transaction Management**: Ensure data consistency

## Exception Hierarchy

```python
ServiceException (base)
├── NotFoundError          # Entity not found by ID
├── AlreadyExistsError     # Unique constraint violation
├── AuthenticationError    # Login/auth failed
├── AuthorizationError     # Permission denied
├── ValidationError        # Business rule violation
└── ConflictError          # State conflict
```

## Base Service

All services inherit from `BaseService` which provides:
- Standard CRUD operations
- Automatic ORM → Pydantic conversion
- Unique constraint checking hook
- Consistent error handling

```python
from src.services.base import BaseService

class MyService(BaseService[Model, CreateSchema, UpdateSchema, ReadSchema]):
    def __init__(self, repository: MyRepository):
        super().__init__(
            repository=repository,
            entity_name="MyEntity",
            create_schema=CreateSchema,
            update_schema=UpdateSchema,
            read_schema=ReadSchema,
        )
```

## Services

### UserService
**Authentication & User Management**

```python
from src.services import UserService
from src.core.dependencies import UserSvc, MainDBSession

async def example(
    user_service: UserSvc,
    db: MainDBSession
):
    # Create user with hashed password
    user = await user_service.create(
        UserCreate(username="john", email="j@ex.com", password="SecurePass1"),
        db
    )
    
    # Authenticate and get tokens
    auth_result = await user_service.authenticate("john", "SecurePass1", db)
    # Returns: {access_token, refresh_token, token_type, user}
    
    # Get by username
    user = await user_service.get_by_username("john", db)
    
    # Deactivate user
    await user_service.deactivate_user(user.id, db)
```

**Features:**
- Password hashing with bcrypt
- JWT token generation
- Username/email uniqueness validation
- Active user filtering
- Account activation/deactivation

### FilmService
**Film Management**

```python
from src.services import FilmService

# Create film
film = await film_service.create(
    FilmCreate(name="Sample Film", coating_thickness=2.5),
    db
)

# Search by name
films = await film_service.search_by_name("Sample", db)
```

**Features:**
- Name uniqueness validation
- Fuzzy name search

### EquipmentConfigService
**Equipment Configuration Management**

```python
# Create config
config = await config_service.create(
    EquipmentConfigCreate(name="Config A", head_type="Type1"),
    db
)

# Get by head type
configs = await config_service.get_by_head_type("Type1", db)
```

**Features:**
- Name uniqueness validation
- Search by name and head type

### ExperimentService
**Experiment Management with Business Logic**

```python
# Create experiment (validates all foreign keys)
experiment = await experiment_service.create(
    ExperimentCreate(
        film_id=film.id,
        config_id=config.id,
        user_id=user.id,
        scratch_indices=[1, 2, 3],
        weight=15.5
    ),
    db
)

# Get experiments by user
user_experiments = await experiment_service.get_by_user_id(user.id, db)

# Get experiment with images
full_experiment = await experiment_service.get_with_images(experiment.id, db)
```

**Features:**
- Foreign key validation (user, film, config)
- Query by user, film, or config
- Load with related images

### ExperimentImageService
**Image Management**

```python
# Create image (validates experiment exists)
image = await image_service.create(
    ExperimentImageCreate(
        experiment_id=experiment.id,
        image_data=image_bytes,
        passes=5
    ),
    db
)

# Get all images for experiment
images = await image_service.get_by_experiment_id(experiment.id, db)

# Delete all images for experiment
count = await image_service.delete_by_experiment_id(experiment.id, db)
```

**Features:**
- Experiment existence validation
- Image size validation (max 10MB)
- Bulk operations

## Error Handling in API

```python
from fastapi import HTTPException
from src.services import NotFoundError, AlreadyExistsError, AuthenticationError

@app.post("/users/")
async def create_user(
    user_data: UserCreate,
    user_service: UserSvc,
    db: MainDBSession
):
    try:
        user = await user_service.create(user_data, db)
        return user
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
```

## Dependency Injection

Services are injected via FastAPI dependencies:

```python
from src.core.dependencies import (
    UserSvc, FilmSvc, ExperimentSvc,
    MainDBSession, UsersDBSession
)

@app.get("/experiments/")
async def list_experiments(
    experiment_service: ExperimentSvc,
    db: MainDBSession,
    skip: int = 0,
    limit: int = 100
):
    return await experiment_service.get_all(db, skip, limit)
```

## Best Practices

1. **Always use services in controllers** - Never access repositories directly
2. **Handle service exceptions** - Convert to HTTP exceptions in API layer
3. **Use dependency injection** - Annotated types for clean code
4. **Keep services focused** - One service per domain entity
5. **Validate foreign keys** - Check existence before creating relationships
6. **Use transactions** - Session commits handled by repository layer

## Transaction Management

Services don't manage transactions directly. The repository layer commits changes:

```python
# In repository:
async def create(self, data: dict, session: AsyncSession):
    stmt = insert(self.model).values(**data).returning(self.model)
    result = await session.execute(stmt)
    await session.commit()  # ← Transaction committed here
    return result.scalar_one()
```

For complex multi-step operations, use `get_db_transaction()` context manager:

```python
from src.core.database import get_db_transaction

async with get_db_transaction() as session:
    # Multiple operations
    user = await user_service.create(user_data, session)
    experiment = await experiment_service.create(exp_data, session)
    # Commits at end of context if no exceptions
```




















