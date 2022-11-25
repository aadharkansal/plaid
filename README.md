# Plaid Project


## Getting started

### Backend

#### 1. Clone repo

- clone the repo using ```git clone https://github.com/aadharkansal/C2C.git```
- Run command ```cd C2C```

#### 2. Create a virtualenv:

- ``` python -m venv venv```
- run the following on terminal``` .\venv\Scripts\activate```
- ``` pip install -r requirements.txt ```

#### 3. Migrations and seeding

- Run command ```python manage.py makemigrations``` to create migrations
- Run command ```python manage.py migrate``` to migrate models on local DB
- Run command ```python manage.py createsuperuser``` to create a admin user

#### 4. Run the django server

- Run command ```python manage.py runserver```
- For admin, click [here](http://localhost:8000/admin/)
- Finally, test the functionality
