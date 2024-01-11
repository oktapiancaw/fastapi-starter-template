FROM python:3.10-slim

WORKDIR /app

COPY dist ./dist

# ? * install all dependencies in dist
RUN pip install ./dist/fastapi_template-0.1.0.tar.gz

CMD ["fastapi-run"]