# Meduzzen Backend

## Local Development

Install poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Clone the repository
```bash
git clone https://github.com/TetyanaPavlyuk/Meduzzen-backend.git
cd Meduzzen_backend
```
Install Dependencies
```bash
poetry install --no-root
```
Create a `.env` file by duplicating `.env.sample` and updating the variable values.

### To run the server locally 
Use the following command
```bash
export $(cat .env | xargs)
uvicorn app.main:app --host $BACKEND_HOST --port $BACKEND_PORT --reload --reload-dir app
```
To run the tests, use the following command
```bash
poetry run pytest
```

### Run with Docker
Docker should be installed and running.
```bash
docker build -t fastapi-app .
docker run --env-file .env -p 8000:8000 --name backend-container fastapi-app

```

To run the tests in docker, use the following command
```bash
docker exec -it backend-container poetry run pytest
```
