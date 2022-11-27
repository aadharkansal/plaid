# Plaid Project


## Getting started

### Backend

#### 1. Clone repo

- clone the repo using ```git clone https://github.com/aadharkansal/plaid.git```
- Run command ```cd plaid```

#### 2. Create a virtualenv:

- ``` python3 -m venv venv```
- run the following on terminal```source venv/bin/activate```
- ``` pip install -r requirements.txt ```

#### 3. Migrations and seeding

- Run command ```python manage.py makemigrations``` to create migrations
- Run command ```python manage.py migrate``` to migrate models on local DB
- Run command ```python manage.py createsuperuser``` to create a admin user

#### 4. Setup Redis

- Run command ```redis-server``` to start redis server

#### 5. Setup Celery

- Run command ```python -m celery -A django_celery worker -l info``` to start celery server

#### 6. Run the django server

- Run command ```python manage.py runserver```
- For admin, click [here](http://localhost:8000/admin/)
- Finally, test the functionality
