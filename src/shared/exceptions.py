from fastapi import HTTPException
from typing import Any

class NotFoundError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)

class BadRequestError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)

class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "No autorizado"):
        super().__init__(status_code=401, detail=detail)
