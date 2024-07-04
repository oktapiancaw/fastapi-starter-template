from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

from src.configs.db import MainPostgre
from src.routes.base import router as api_router
from src.routes.middleware import ProcessTimeMiddleware, RateLimitingMiddleware
from src.models.post import Base


def get_application() -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.postgre = MainPostgre()
        app.state.postgre.connect()
        Base.metadata.create_all(app.state.postgre.engine)
        yield
        app.state.postgre.close()

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
    application.add_middleware(RateLimitingMiddleware)
    application.add_middleware(ProcessTimeMiddleware)

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
