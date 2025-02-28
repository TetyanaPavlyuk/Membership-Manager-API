# Meduzzen Backend

## Local Development

#### To run the server locally, use the following command
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```


#### To run the tests, use the following command
```bash
poetry run pytest
```

#### Run with Docker
Docker should be installed
```bash
docker build -t fastapi-app .
docker run -d -p 8000:8000 --name backend-container fastapi-app
```

#### To run the tests in docker, use the following command
```bash
docker exec -it backend-container poetry run pytest
```
