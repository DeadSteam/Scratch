# Pydantic Schemas Documentation

## Overview
Pydantic v2 schemas with validation for all domain models.

## Schema Organization

Each domain entity has 4 schema types following SOLID principles:

- **Base**: Common fields shared between Create/Update/Read
- **Create**: Input schema for creating new entities (includes required fields)
- **Update**: Input schema for updating (all fields optional)
- **Read**: Output schema for API responses (includes ID and relationships)

## Validation Rules

### User Schemas
- **Username**: 3-50 characters, alphanumeric with underscores, auto-lowercased
- **Email**: Valid email format (EmailStr)
- **Password**: Min 8 characters, requires uppercase, lowercase, and digit

### Film Schemas
- **Name**: 1-100 characters, required
- **Coating thickness**: Must be positive, required if coating_name is provided
- **Coating name**: Max 100 characters

### Equipment Config Schemas
- **Name**: 1-100 characters, required
- **Head type**: Max 100 characters, optional
- **Description**: Unlimited length, optional

### Experiment Schemas
- **Scratch indices**: Must be non-negative, unique integers
- **Rectangle coords**: Exactly 4 values [x, y, width, height], all non-negative
- **Weight**: Must be positive (grams)
- **Has fabric**: Boolean flag

### Experiment Image Schemas
- **Image data**: Max 10MB, cannot be empty
- **Passes**: 1-100 range

## Usage Examples

### Creating a User
```python
from src.schemas import UserCreate

user_data = UserCreate(
    username="john_doe",
    email="john@example.com",
    password="SecurePass123"
)
```

### Validating Experiment Data
```python
from src.schemas import ExperimentCreate
from uuid import UUID

experiment_data = ExperimentCreate(
    film_id=UUID("..."),
    config_id=UUID("..."),
    user_id=UUID("..."),
    scratch_indices=[1, 3, 5],
    rect_coords=[10.5, 20.0, 100.0, 50.0],
    weight=15.5,
    has_fabric=True
)
```

### Updating Film
```python
from src.schemas import FilmUpdate

film_update = FilmUpdate(
    coating_thickness=2.5  # Only update thickness
)
```

## Field Validators

All schemas use Pydantic v2 `@field_validator` decorator for custom validation:

- **@field_validator('field_name')**: Validates individual fields
- **mode='after'**: Validation runs after Pydantic's built-in validators
- **ValidationInfo**: Access to other validated fields via `info.data`

## Serialization

All schemas inherit from `SchemaBase` with:
- `from_attributes=True`: Convert SQLAlchemy models to Pydantic
- `populate_by_name=True`: Accept both field names and aliases

### Converting ORM to Schema
```python
from src.models import User
from src.schemas import UserRead

user_orm = await session.get(User, user_id)
user_schema = UserRead.model_validate(user_orm)
```

### JSON Serialization
```python
user_json = user_schema.model_dump_json()
user_dict = user_schema.model_dump()
```




















