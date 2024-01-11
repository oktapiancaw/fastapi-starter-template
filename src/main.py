from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

from src.configs.db import MainMongo
from src.routes.base import router as api_router


def get_application() -> FastAPI:
    # _app_name = "importlib.metadata.metadata(_app_name)"
    # _app_title = importlib.metadata.metadata(_app_name).get("Name").replace("-", " ").title()
    # _app_version = importlib.metadata.metadata(_app_name).get("Version")
    # _app_contact = {
    #     'name': importlib.metadata.metadata(_app_name).get("Author"),
    #     'email': importlib.metadata.metadata(_app_name).get("Author-email")
    # }
    # _app_description = importlib.metadata.metadata(_app_name).get("Summary")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.mongo = MainMongo()
        yield
        app.state.mongo.close()

    application = FastAPI(
        docs_url="/",
        title="Fastapi Template",
        debug=False,
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)

    @application.get("/rapidoc", response_class=HTMLResponse, include_in_schema=False)
    async def rapidoc():
        return f"""
            <!doctype html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <script 
                        type="module" 
                        src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"
                    ></script>
                </head>
                <body>
                    <rapi-doc spec-url="{application.openapi_url}"></rapi-doc>
                </body> 
            </html>
        """

    return application


app = get_application()


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)
