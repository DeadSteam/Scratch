# API Documentation

## Overview
RESTful API built with FastAPI for experiment management system.

## Base URL
```
http://localhost:8000/api/v1
```

## API Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

## Architecture

```
API Endpoints → Exception Handlers → Services → Repositories → Database
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { /* response data */ }
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [ /* list of items */ ],
  "total": 100,
  "skip": 0,
  "limit": 50,
  "has_more": true
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "errors": [
    {
      "field": "username",
      "message": "Field is required",
      "type": "missing"
    }
  ],
  "detail": { /* additional error context */ }
}
```

## HTTP Status Codes

- `200 OK` - Successful GET/PATCH request
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Unique constraint violation
- `422 Unprocessable Entity` - Schema validation error
- `500 Internal Server Error` - Server error

## Authentication

### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "is_active": true,
    "roles": []
  }
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "user": { /* user object */ }
  }
}
```

## Users

### List Users
```http
GET /api/v1/users?skip=0&limit=50
```

### Get User by ID
```http
GET /api/v1/users/{user_id}
```

### Get User by Username
```http
GET /api/v1/users/username/{username}
```

### Update User
```http
PATCH /api/v1/users/{user_id}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "is_active": true
}
```

### Deactivate User
```http
POST /api/v1/users/{user_id}/deactivate
```

### Delete User
```http
DELETE /api/v1/users/{user_id}
```

## Films

### List Films
```http
GET /api/v1/films?skip=0&limit=50
```

### Search Films by Name
```http
GET /api/v1/films/search?name=sample&skip=0&limit=50
```

### Get Film by ID
```http
GET /api/v1/films/{film_id}
```

### Create Film
```http
POST /api/v1/films
Content-Type: application/json

{
  "name": "Sample Film",
  "coating_name": "Gold",
  "coating_thickness": 2.5
}
```

### Update Film
```http
PATCH /api/v1/films/{film_id}
Content-Type: application/json

{
  "coating_thickness": 3.0
}
```

### Delete Film
```http
DELETE /api/v1/films/{film_id}
```

## Equipment Configurations

### List Configs
```http
GET /api/v1/equipment-configs?skip=0&limit=50
```

### Search by Name
```http
GET /api/v1/equipment-configs/search?name=config&skip=0&limit=50
```

### Get by Head Type
```http
GET /api/v1/equipment-configs/head-type/{head_type}?skip=0&limit=50
```

### Get Config by ID
```http
GET /api/v1/equipment-configs/{config_id}
```

### Create Config
```http
POST /api/v1/equipment-configs
Content-Type: application/json

{
  "name": "Config A",
  "head_type": "Type 1",
  "description": "Configuration description"
}
```

### Update Config
```http
PATCH /api/v1/equipment-configs/{config_id}
Content-Type: application/json

{
  "description": "Updated description"
}
```

### Delete Config
```http
DELETE /api/v1/equipment-configs/{config_id}
```

## Experiments

### List Experiments
```http
GET /api/v1/experiments?skip=0&limit=50
```

### Get by User
```http
GET /api/v1/experiments/user/{user_id}?skip=0&limit=50
```

### Get by Film
```http
GET /api/v1/experiments/film/{film_id}?skip=0&limit=50
```

### Get by Config
```http
GET /api/v1/experiments/config/{config_id}?skip=0&limit=50
```

### Get Experiment by ID
```http
GET /api/v1/experiments/{experiment_id}
```

### Get Experiment with Images
```http
GET /api/v1/experiments/{experiment_id}/with-images
```

### Create Experiment
```http
POST /api/v1/experiments
Content-Type: application/json

{
  "film_id": "uuid",
  "config_id": "uuid",
  "user_id": "uuid",
  "date": "2024-01-01T12:00:00Z",
  "scratch_indices": [1, 2, 3],
  "rect_coords": [10.0, 20.0, 100.0, 50.0],
  "weight": 15.5,
  "has_fabric": true
}
```

### Update Experiment
```http
PATCH /api/v1/experiments/{experiment_id}
Content-Type: application/json

{
  "weight": 16.0
}
```

### Delete Experiment
```http
DELETE /api/v1/experiments/{experiment_id}
```

## Experiment Images

### Get Images by Experiment
```http
GET /api/v1/images/experiment/{experiment_id}?skip=0&limit=50
```

### Get Image by ID
```http
GET /api/v1/images/{image_id}
```

### Upload Image (Multipart)
```http
POST /api/v1/images/upload?experiment_id={uuid}&passes=5
Content-Type: multipart/form-data

file: <binary image data>
```

### Create Image (JSON)
```http
POST /api/v1/images
Content-Type: application/json

{
  "experiment_id": "uuid",
  "image_data": "<base64 encoded image>",
  "passes": 5
}
```

### Delete Image
```http
DELETE /api/v1/images/{image_id}
```

### Delete All Experiment Images
```http
DELETE /api/v1/images/experiment/{experiment_id}/all
```

**Response (200):**
```json
{
  "success": true,
  "message": "Deleted 5 images",
  "data": {
    "deleted_count": 5
  }
}
```

## Error Handling

### Validation Error Example
```json
{
  "success": false,
  "message": "Validation error",
  "errors": [
    {
      "field": "password",
      "message": "Password must be at least 8 characters",
      "type": "value_error"
    }
  ]
}
```

### Not Found Error Example
```json
{
  "success": false,
  "message": "User with id 123e4567-e89b-12d3-a456-426614174000 not found",
  "detail": {
    "entity": "User",
    "id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### Already Exists Error Example
```json
{
  "success": false,
  "message": "User with username='john_doe' already exists",
  "detail": {
    "entity": "User",
    "field": "username",
    "value": "john_doe"
  }
}
```

## Query Parameters

### Pagination
- `skip` (int, default=0): Number of items to skip
- `limit` (int, default=100, max=1000): Number of items to return

### Search
- `name` (string): Search pattern for name fields

## Best Practices

1. **Always check response status** - Check `success` field before processing data
2. **Handle pagination** - Use `has_more` to determine if more pages exist
3. **Validate input** - API will return 422 for schema validation errors
4. **Handle errors gracefully** - Parse `errors` array for field-specific issues
5. **Use proper HTTP methods** - GET (read), POST (create), PATCH (update), DELETE (delete)

## Testing with cURL

### Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}'
```

### Create Film
```bash
curl -X POST http://localhost:8000/api/v1/films \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Film","coating_thickness":2.5}'
```

### List Films
```bash
curl http://localhost:8000/api/v1/films?limit=10
```

## Testing with httpx (Python)
```python
import httpx

async with httpx.AsyncClient() as client:
    # Register
    response = await client.post(
        "http://localhost:8000/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )
    print(response.json())
    
    # Login
    response = await client.post(
        "http://localhost:8000/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    tokens = response.json()["data"]
    
    # Use access token for authenticated requests
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
```





















