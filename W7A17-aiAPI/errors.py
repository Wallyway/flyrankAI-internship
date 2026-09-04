from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str


BAD_REQUEST = {"model": ErrorResponse, "description": "Missing or rejected fields"}
UNAUTHORIZED = {"model": ErrorResponse, "description": "Access token missing, invalid or expired"}
UNPROCESSABLE = {"model": ErrorResponse, "description": "The model could not produce an answer matching the schema"}
GATEWAY_TIMEOUT = {"model": ErrorResponse, "description": "The model took too long to answer"}
