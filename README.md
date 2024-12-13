# MyRealEstate
A property management application

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js and npm
- Docker (for MinIO)

### Initial Setup

1. Create and activate virtual environment:
```
python
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

1. Install dependencies:
```
pip install -r requirements.txt
```

1. Configure environment variables:
```
# No variables needed for now
```

1. Run database migrations:
```
python manage.py migrate
```
### Tailwind CSS Setup

1. Install Tailwind dependencies:

1. Run the development server:
```
python manage.py runserver
```

