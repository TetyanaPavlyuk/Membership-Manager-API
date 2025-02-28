FROM python:3.12-alpine3.21

# add bash for alpine
RUN apk add --no-cache curl bash

# install poetry
ENV POETRY_HOME=/root/.local
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry

# set the environment variable for the virtual environment
ENV PATH="$POETRY_HOME/bin:$PATH"

# create working directory
WORKDIR /app

# copy dependency files
COPY poetry.lock /app/
COPY pyproject.toml /app/

# disable virtual environment Poetry
RUN poetry config virtualenvs.create false

# install dependencies and create virtual environment
RUN poetry install --no-root

# copy the source code
COPY ./app /app/

# run server
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
