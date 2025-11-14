# Simple Makefile helpers for this Django project

# --------------------------------------------------------------------
# Configurable commands
# --------------------------------------------------------------------
PYTHON := python
MANAGE := $(PYTHON) manage.py
ISORT  := isort

# Common isort exclusions: venvs, git, node_modules, Django migrations, etc.
ISORT_EXCLUDES := \
	--skip .venv \
	--skip venv \
	--skip env \
	--skip node_modules \
	--skip .git \
	--skip-glob "*/migrations/*"

# Default target
.DEFAULT_GOAL := help

.PHONY: isort isort_dry_run clean test coverage makemigrations migrate \
        makemigrate runserver run createuser superuser shell delete_db \
        resetdb seed lint help

# --------------------------------------------------------------------
# Formatting / Linting
# --------------------------------------------------------------------

# Run isort in dry-run mode (no changes, just diff) on real code only
# Excludes virtualenvs, git, node_modules, and Django migrations
isort_dry_run:
	$(ISORT) $(ISORT_EXCLUDES) --check-only --diff .

# Run isort and actually sort imports in-place
isort:
	$(ISORT) $(ISORT_EXCLUDES) .

# Basic lint target (extend with flake8/black later if you like)
lint: isort_dry_run
	@echo "Linting complete (isort only for now)."

# --------------------------------------------------------------------
# Cleaning
# --------------------------------------------------------------------

# Clean python, pytest, and coverage files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	@echo "Cleaned caches and bytecode."

# --------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------

# Run unit tests with Django's test runner
test:
	$(MANAGE) test

# Run tests with coverage + HTML report
coverage:
	coverage run manage.py test && \
	coverage report && \
	coverage html

# --------------------------------------------------------------------
# Database / Migrations
# --------------------------------------------------------------------

# Run makemigrations
makemigrations:
	$(MANAGE) makemigrations

# Run migrate
migrate:
	$(MANAGE) migrate

# Run makemigrations and migrate
makemigrate: makemigrations migrate

# Delete the local SQLite database
delete_db:
	rm -f db.sqlite3
	@echo "Database deleted."

# Delete the DB, recreate it, run migrations, and create superuser
resetdb: delete_db
	@echo "Database and caches cleared."
	$(MAKE) makemigrate
	$(MAKE) createuser

# Load initial data fixtures (adjust fixture name as needed)
seed:
	$(MANAGE) loaddata initial_data

# --------------------------------------------------------------------
# App / Shell helpers
# --------------------------------------------------------------------

# Run the development server
runserver:
	$(MANAGE) runserver

# Convenience alias
run: runserver

# Create superuser from .env values (custom management command)
createuser:
	$(MANAGE) create_user

# Convenience alias
superuser: createuser

# Start the Django shell
shell:
	$(MANAGE) shell

# --------------------------------------------------------------------
# Help
# --------------------------------------------------------------------

# Show this help
help:
	@echo "Available targets:"
	@awk '/^[a-zA-Z0-9_%-]+:/ { \
		if (match(prev, /^# (.+)/, desc)) { \
			printf "  \033[1m%-15s\033[0m %s\n", $$1, desc[1]; \
		} else { \
			printf "  \033[1m%-15s\033[0m\n", $$1; \
		} \
	} { prev = $$0 }' $(MAKEFILE_LIST)
