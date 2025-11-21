# Plan-It Mini API Documentation

This document provides an overview of the REST API implemented for the Plan-It Mini project.

## Base URL

All API endpoints are available at `/api/` when the server is running.

## Authentication

The API uses HTTP Basic Authentication or Session Authentication. All endpoints require authentication.

### Example using curl:
```bash
curl -u username:password http://localhost:8000/api/workspaces/
```

## Permissions

- **Read Operations (GET)**: Any authenticated user
- **Write Operations (POST/PUT/PATCH/DELETE)**: 
  - Staff users (full access)
  - Users in the `maintenance_manager` group (full access)
  - Workspace managers/admins (access to their workspace resources only)

## Throttling

Non-staff users are limited to 1000 requests per day. Staff users have unlimited access.

## Pagination

All list endpoints are paginated with 20 items per page by default. The response includes:
- `count`: Total number of items
- `next`: URL to the next page (null if none)
- `previous`: URL to the previous page (null if none)
- `results`: Array of items for the current page

## Available Endpoints

### Core

#### Workspaces
- **GET /api/workspaces/** - List all workspaces (filtered by user membership)
- **POST /api/workspaces/** - Create a new workspace
- **GET /api/workspaces/{id}/** - Get workspace details
- **PUT/PATCH /api/workspaces/{id}/** - Update workspace
- **DELETE /api/workspaces/{id}/** - Delete workspace

**Filters**: None
**Search**: name, slug
**Ordering**: name

#### Memberships
- **GET /api/memberships/** - List all memberships
- **POST /api/memberships/** - Create a new membership
- **GET /api/memberships/{id}/** - Get membership details
- **PUT/PATCH /api/memberships/{id}/** - Update membership
- **DELETE /api/memberships/{id}/** - Delete membership

**Search**: user__username, workspace__name, role
**Ordering**: workspace__name, user__username, role

### Assets

#### Form Factors
- **GET /api/form-factors/** - List all form factors
- **POST /api/form-factors/** - Create a new form factor
- **GET /api/form-factors/{id}/** - Get form factor details
- **PUT/PATCH /api/form-factors/{id}/** - Update form factor
- **DELETE /api/form-factors/{id}/** - Delete form factor

**Search**: name, slug
**Ordering**: name

#### Operating Systems
- **GET /api/oses/** - List all operating systems
- **POST /api/oses/** - Create a new OS
- **GET /api/oses/{id}/** - Get OS details
- **PUT/PATCH /api/oses/{id}/** - Update OS
- **DELETE /api/oses/{id}/** - Delete OS

**Search**: name, version, slug
**Ordering**: name, version

#### Applications
- **GET /api/applications/** - List all applications
- **POST /api/applications/** - Create a new application
- **GET /api/applications/{id}/** - Get application details
- **PUT/PATCH /api/applications/{id}/** - Update application
- **DELETE /api/applications/{id}/** - Delete application

**Search**: name, version, slug
**Ordering**: name, version

#### Projects
- **GET /api/projects/** - List all projects (filtered by user workspace membership)
- **POST /api/projects/** - Create a new project
- **GET /api/projects/{id}/** - Get project details
- **PUT/PATCH /api/projects/{id}/** - Update project
- **DELETE /api/projects/{id}/** - Delete project

**Search**: name, slug, workspace__name
**Ordering**: name

#### Assets
- **GET /api/assets/** - List all assets (filtered by user workspace membership)
- **POST /api/assets/** - Create a new asset
- **GET /api/assets/{id}/** - Get asset details (includes nested applications)
- **PUT/PATCH /api/assets/{id}/** - Update asset
- **DELETE /api/assets/{id}/** - Delete asset

**Filters**:
- `form_factor` - Filter by form factor ID
- `os` - Filter by OS ID
- `applications` - Filter by application ID
- `location` - Exact match on location
- `warranty_expires__lt` - Warranty expires before date (YYYY-MM-DD)
- `name__icontains` - Case-insensitive substring match on name

**Search**: name, location, notes
**Ordering**: name, purchase_date, warranty_expires

**Example**:
```bash
# Get all assets with warranty expiring before 2025-12-31
curl -u user:pass "http://localhost:8000/api/assets/?warranty_expires__lt=2025-12-31"

# Search for assets with "server" in the name
curl -u user:pass "http://localhost:8000/api/assets/?name__icontains=server"
```

### Work

#### Maintenance Tasks
- **GET /api/maintenance-tasks/** - List all maintenance tasks
- **POST /api/maintenance-tasks/** - Create a new task
- **GET /api/maintenance-tasks/{id}/** - Get task details
- **PUT/PATCH /api/maintenance-tasks/{id}/** - Update task
- **DELETE /api/maintenance-tasks/{id}/** - Delete task

**Search**: name, cadence, workspace__name
**Ordering**: name, cadence

#### Work Orders
- **GET /api/work-orders/** - List all work orders (filtered by user workspace membership)
- **POST /api/work-orders/** - Create a new work order
- **GET /api/work-orders/{id}/** - Get work order details
- **PUT/PATCH /api/work-orders/{id}/** - Update work order
- **DELETE /api/work-orders/{id}/** - Delete work order

**Filters**:
- `asset` - Filter by asset ID
- `task` - Filter by task ID
- `status` - Filter by status (open, done, cancelled)
- `due__date_after` - Due date after (YYYY-MM-DD)
- `due__date_before` - Due date before (YYYY-MM-DD)

**Search**: asset__name, task__name, assigned_to__username, requested_by__username
**Ordering**: due (default: descending), status

**Example**:
```bash
# Get open work orders due in January 2025
curl -u user:pass "http://localhost:8000/api/work-orders/?status=open&due__date_after=2025-01-01&due__date_before=2025-01-31"
```

#### Activity Instances
- **GET /api/activities/** - List all activities (filtered by user workspace membership)
- **POST /api/activities/** - Create a new activity
- **GET /api/activities/{id}/** - Get activity details
- **PUT/PATCH /api/activities/{id}/** - Update activity
- **DELETE /api/activities/{id}/** - Delete activity

**Filters**:
- `asset` - Filter by asset ID
- `kind` - Filter by kind (checked, patched, backup_verified)
- `occurred_at_after` - Occurred after date (YYYY-MM-DD)
- `occurred_at_before` - Occurred before date (YYYY-MM-DD)

**Search**: asset__name, note, performed_by__username
**Ordering**: occurred_at (default: descending)

**Example**:
```bash
# Get all activities for an asset in the last 30 days
curl -u user:pass "http://localhost:8000/api/activities/?asset=3&occurred_at_after=2025-10-01"
```

## Response Format

### Success Response
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Example",
      ...
    }
  ]
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Workspace Scoping

Non-staff users can only access resources from workspaces they are members of. This applies to:
- Workspaces
- Projects
- Assets
- Maintenance Tasks
- Work Orders
- Activity Instances

Staff users can access all resources across all workspaces.

## Examples

### List workspaces
```bash
curl -u testuser:testpass http://localhost:8000/api/workspaces/
```

### Get asset with nested applications
```bash
curl -u testuser:testpass http://localhost:8000/api/assets/1/
```

### Filter assets by warranty expiration
```bash
curl -u testuser:testpass "http://localhost:8000/api/assets/?warranty_expires__lt=2025-12-31"
```

### Create a new work order
```bash
curl -u testuser:testpass \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "workspace": "test-ws",
    "asset": 1,
    "task": 1,
    "due": "2025-12-31T23:59:59Z",
    "status": "open"
  }' \
  http://localhost:8000/api/work-orders/
```

## Development

To test the API in development:

1. Start the development server:
   ```bash
   pipenv run python manage.py runserver
   ```

2. Access the browsable API at `http://localhost:8000/api/`

3. Create a test user:
   ```bash
   pipenv run python manage.py createsuperuser
   ```

## Testing

Run the API tests:
```bash
pipenv run pytest api/tests.py -v
```
