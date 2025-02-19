# MyRealEstate
A property management application

## Setup and Installation

There are two ways to set up the project: using Docker (recommended) or local setup.

### Option 1: Docker Setup (Recommended)

1. Prerequisites:
   - Docker
   - Docker Compose

2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd MyRealEstate
   ```

3. Start the application:
   ```bash
   docker-compose up --build
   ```

4. The following services will be available:
   - Django application: http://localhost:8000
   - MinIO Console: http://localhost:9001
   - Mailpit UI: http://localhost:8025
   - Tailwind CSS: http://localhost:8383

5. Create migrations
   ```
   docker compose exec web python manage.py migrate
   ```

### Option 2: Local Setup

#### Prerequisites
- Python 3.8+
- Node.js and npm
- PostgreSQL
- MinIO (for object storage)

#### Initial Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   export DEBUG=True
   export DJANGO_SETTINGS_MODULE=myrealestate.config.settings
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
   export MINIO_ACCESS_KEY=minio_access_key
   export MINIO_SECRET_KEY=minio_secret_key
   export MINIO_BUCKET_NAME=mre-app-bucket
   export MINIO_ENDPOINT=localhost:9000
   ```

4. Run database migrations:
   ```bash
   python manage.py migrate
   ```

5. Install Tailwind dependencies:
   ```bash
   python manage.py tailwind install
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. In a separate terminal, start Tailwind CSS:
   ```bash
   python manage.py tailwind start
   ```

## Development

- The application will be available at http://localhost:8000
- MinIO console can be accessed at http://localhost:9001
- Mailpit UI is available at http://localhost:8025
- Tailwind CSS live reload runs on http://localhost:8383


