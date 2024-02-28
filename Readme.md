# Description

[![python: v^3.10](https://img.shields.io/badge/python-v^3.10-333A73.svg?logo=python&style=for-the-badge&logoColor=ffffff)](https://www.python.org/downloads/release/python-3100/)
[![Fastapi: v^0.108.0](https://img.shields.io/badge/fastapi-v^0.108.0-009485.svg?logo=fastapi&style=for-the-badge&logoColor=ffffff)](https://fastapi.tiangolo.com/)
[![Pydantic: v^2.4.2](https://img.shields.io/badge/pydantic-v^2.4.2-e92063.svg?logo=pydantic&style=for-the-badge&logoColor=ffffff)](https://pydantic.dev)

This project is only intended for fastapi templates, which consist of simple things, such as file placement, data modeling, how to respond to data, and connecting to the database.

All of that is just our version, if anyone has suggestions, you can make an issue, hopefully this project can help you in your work.

# Project Setup
This project was created with poetry, we suggest learning [Poetry](https://python-poetry.org/) first, if not, use the manual option
### Initialization
There are 2 options to initialize the project

- using poetry :

```bash
poetry env use 3.10
source $(poetry env info --path)/bin/activate
poetry install
```

- or manual :

```bash
pip install -r requirements.txt
```

### Run the app
To run it, you can use the command

- poetry script :

```bash
fastapi-run
```

- manual :
```
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
# or
python src/main.py
```

Then you can access on :
```
# Swagger doc
0.0.0.0:8000
# Redoc
0.0.0.0:8000/redoc
```

## Depedencies

### Getting started with Poetry
Let build your own python environment [Basic Guide](https://python-poetry.org/docs/basic-usage/)

### Getting started with Pydantic
Let create your first model using pydantic from [Basic Usage](https://docs.pydantic.dev/latest/#pydantic-examples)

We also have repository that can be used as references in creating models :

- [Typica](https://github.com/oktapiancaw/module-typica)

### Getting started with Fastapi
Let create your first service on [User Guide](https://fastapi.tiangolo.com/tutorial/)


## Contributors

[//]: contributor-faces

<a href="https://github.com/oktapiancaw"><img src="https://avatars.githubusercontent.com/u/48079010?v=4" title="Oktapian Candra" width="80" height="80" style="border-radius: 50%"></a>

[//]: contributor-faces