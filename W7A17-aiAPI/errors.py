from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str


BAD_REQUEST = {"model": ErrorResponse, "description": "Missing or rejected fields"}
UNAUTHORIZED = {"model": ErrorResponse, "description": "Access token missing, invalid or expired"}
