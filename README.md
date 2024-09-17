## To start app follow next steps

### 1. start virtual env
### 2. install requirements - pip install requirements.txt
### 3. create docker container with PostgreSQL database - docker-compose up -d
### 4. test connection to database and in case of success run migrations to create tables - alembic upgrade head
### 5. start app - uvicorn app.main:app --reload --port 8080
