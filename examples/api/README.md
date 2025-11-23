# Manual API Examples

These scripts show quick ways to inspect the Plan-It API by hand.

## Setup
- Run the Django server locally.
- Create a user with access.
- Add creds to `.env`:

PLANIT_BASE_URL=http://127.0.0.1:8000
PLANIT_USERNAME=admin
PLANIT_PASSWORD=yourpassword

## Run
python examples/api/maintenance_tasks.py
python examples/api/assets.py
python examples/api/workspaces.py
