# Development Commands

## Docker Container Management

```
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Rebuild containers
docker compose up -d --build

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f web
```

## Django Management Commands
```
# Make migrations
docker compose exec web python manage.py makemigrations

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Shell
docker compose exec web python manage.py shell

# Create new app
docker compose exec web python manage.py startapp app_name

# Show migrations
docker compose exec web python manage.py showmigrations
```

## Package Management
```
# Install Python package
docker compose exec web pip install package_name

# Update requirements.txt after installing packages
docker compose exec web pip freeze > requirements.txt

# Install npm package
docker compose exec tailwind npm install package_name

# Install npm package as dev dependency
docker compose exec tailwind npm install --save-dev package_name
```

## Tailwind Commands
```
# Install Tailwind dependencies
docker compose exec web python manage.py tailwind install

# Start Tailwind in watch mode
docker compose exec web python manage.py tailwind start

# Build Tailwind for production
docker compose exec web python manage.py tailwind build
```

## Testing
```
# Run all tests
docker compose exec web python manage.py test

# Run specific test file
docker compose exec web python manage.py test app_name.tests.test_file

# Run specific test class
docker compose exec web python manage.py test app_name.tests.test_file.TestClass

# Run specific test method
docker compose exec web python manage.py test app_name.tests.test_file.TestClass.test_method
```

## Coverage
```
# Run tests with coverage
docker compose exec web coverage run manage.py test

# Generate coverage report
docker compose exec web coverage report

# Generate HTML coverage report
docker compose exec web coverage html

# Show specific file coverage
docker compose exec web coverage report -m path/to/file.py
```

## Database Operations
```
# Create database backup
docker compose exec db pg_dump -U postgres postgres > backup.sql

# Restore database
docker compose exec -T db psql -U postgres postgres < backup.sql

# Access PostgreSQL shell
docker compose exec db psql -U postgres
```

## Minio Operations
```
# Create a new bucket
docker compose exec minio mc mb /data/bucket-name

# List all buckets
docker compose exec minio mc ls /data

# Set bucket policy to public
docker compose exec minio mc policy set public /data/bucket-name
```

## Cleaning Up
```
# Remove all stopped containers
docker compose rm -f

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove all unused Docker resources
docker system prune -a
```

## Production Deployment Commands
```
# Collect static files for production
docker compose exec web python manage.py collectstatic --noinput --clear

# Check for deployment issues
docker compose exec web python manage.py check --deploy

# Run migrations on production
docker compose exec web python manage.py migrate --noinput
```

## Development Utilities
```
# Generate model diagram
docker compose exec web python manage.py graph_models -a -o models.png

# Show URLs
docker compose exec web python manage.py show_urls

# Clear cache
docker compose exec web python manage.py clear_cache

# Create initial data
docker compose exec web python manage.py loaddata fixtures/initial_data.json
```

## Environment Management
```
# View environment variables
docker compose exec web printenv

# Run command with specific environment
docker compose exec -e DJANGO_SETTINGS_MODULE=myrealestate.config.settings.production web python manage.py check
```

## Debugging
```
# Check Django version
docker compose exec web python -m django --version

# Check installed packages
docker compose exec web pip list

# Check system resources
docker stats

# View Docker container details
docker inspect container_name
```
