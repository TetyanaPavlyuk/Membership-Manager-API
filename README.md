# Meduzzen Backend

## Local Development

To run the server locally, use the following command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```


To run the tests, use the following command:

```bash
poetry run pytest
```
