from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

import config
from access_routes import router as access_router
from auth_routes import router as auth_router
from auth_service import AuthService
from llm.client import LLMClient
from llm.service import TriageService
from repo_postgres import PostgresTaskRepository
from repo_sqlite import SqliteTaskRepository
from routes import router
from service import TaskService
from triage_routes import router as triage_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server running and connected to Supabase")
    yield


tags_metadata = [
    {"name": "auth", "description": "Sign up, log in and log out through Supabase."},
    {"name": "public", "description": "Open to anyone, no token needed."},
    {"name": "protected", "description": "Require an access token. Click Authorize and paste the one returned by /auth/login."},
    {"name": "tasks", "description": "The CRUD API from the previous assignment."},
    {"name": "triage", "description": "Classifies a free-text task description with an LLM, and returns validated JSON."},
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


def build_auth():
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        return None
    return AuthService(config.SUPABASE_URL, config.SUPABASE_KEY)


app.state.service = TaskService(build_repository())
app.state.auth = build_auth()
def build_llm_client():
    return LLMClient(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.LLM_MODEL,
        timeout=config.LLM_TIMEOUT_SECONDS,
        max_attempts=config.LLM_MAX_ATTEMPTS,
    )


app.state.triage = TriageService(
    config.LLM_STUB,
    config.LLM_ENABLED,
    build_llm_client(),
    config.PROMPT_VERSION,
    config.QUARANTINE_PATH,
)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


def describe_validation_error(error: dict) -> str:
    location = [str(part) for part in error["loc"] if part != "body"]
    field = ".".join(location) if location else "body"
    return f"{field}: {error['msg']}"


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = [describe_validation_error(error) for error in exc.errors()]
    return JSONResponse(status_code=400, content={"error": "; ".join(details)})


app.include_router(auth_router)
app.include_router(access_router)
app.include_router(triage_router)
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
