# Archangel

## SQL-schema:
https://drawsql.app/teams/pkb/diagrams/archangel


How to start
------------

1. Create .env
`  SECRET_KEY=
   DEBUG=
   DB_NAME=
   DB_USER=
   DB_PASSWORD=
   DB_HOST=localhost 
   DB_PORT=`
   DB_HOST can be changed on deploying 

2. Install requirements.
    ```bash
    pip install -r requirements.txt
    ```
3. Create database and apply migrations.
    ```bash
    python manage.py migrate
    ```
4. Create superuser.
    ```bash
    python manage.py createsuperuser
    ```
5. Run server.
    ```bash
    python manage.py runserver
    ```
   
How to start with docker 
------------------------
```bash
docker-compose up --build
```
in .env change HOST to 'db' 