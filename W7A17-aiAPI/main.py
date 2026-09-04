from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

import config
from access_routes import router as access_router
from auth_routes import router as auth_router
from auth_service import AuthService
from repo_postgres import PostgresTaskRepository
from repo_sqlite import SqliteTaskRepository
from routes import router
from service import TaskService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server running and connected to Supabase")
    yield


tags_metadata = [
    {"name": "auth", "description": "Sign up, log in and log out through Supabase."},
    {"name": "public", "description": "Open to anyone, no token needed."},
    {"name": "protected", "description": "Require an access token. Click Authorize and paste the one returned by /auth/login."},
    {"name": "tasks", "description": "The CRUD API from the previous assignment."},
]

app = FastAPI(
    title="Task API",
    version="2.0",
    description="A CRUD API for managing tasks, with Supabase authentication protecting private routes.",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


def build_repository():
    if config.DB_BACKEND == "postgres":
        return PostgresTaskRepository(config.DATABASE_URL)
    return SqliteTaskRepository(config.SQLITE_PATH)


app.state.service = TaskService(build_repository())
app.state.auth = AuthService(config.SUPABASE_URL, config.SUPABASE_KEY)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


app.include_router(auth_router)
app.include_router(access_router)
app.include_router(router)


def build_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        tags=tags_metadata,
        routes=app.routes,
    )
    for operations in schema["paths"].values():
        for operation in operations.values():
            operation["responses"].pop("422", None)
    app.openapi_schema = schema
    return schema


app.openapi = build_openapi
