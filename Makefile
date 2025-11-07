.PHONY: isort_dry_run clean test coverage makemigrations migrate makemigrate runserver createuser shell delete_db resetdb

# Run isort
# TODO: Exclude migration files-
isort_dry_run:
	isort --check-only --diff .

# Clean python, pytest, and coverage files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.coverage" -delete
	echo "Cleaned __pycache__, .pytest_cache, and htmlcov directories and .pyc, .coverage files."

# Run unit tests
test:
	python manage.py test

# Run pytest with coverage
coverage:
	coverage run manage.py test && \
	coverage report && \
	coverage html

# Run makemigrations
makemigrations:
	python manage.py makemigrations

# Run migrate
migrate:
	python manage.py migrate

# Run makemigrations and migrate
makemigrate: makemigrations migrate

# Run the development server
runserver:
	python manage.py runserver

# Create superuser from .env values
createuser:
	@python manage.py create_user

# Start the Django shell
shell:
	python manage.py shell

# Delete the database
delete_db:
	rm -f db.sqlite3
	echo "Database deleted."
	
# Delete the database and recreate it, add superuser
resetdb:
	rm -f db.sqlite3
	echo "Database and caches cleared."
	make makemigrate
	make createuser

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
