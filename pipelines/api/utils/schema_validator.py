import jsonschema
from jsonschema import validate as jsonschema_validate, ValidationError
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Any
from datetime import datetime


class AuthLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: Optional[int] = 3600
    token_type: Optional[str] = "Bearer"


class AuthRefreshResponse(BaseModel):
    access_token: str
    expires_in: Optional[int] = 3600
    token_type: Optional[str] = "Bearer"


class ErrorResponse(BaseModel):
    error: str
    message: Optional[str] = None
    code: Optional[int] = None


class EntityCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Optional[dict] = None


class EntityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EntityListResponse(BaseModel):
    items: List[EntityResponse]
    total: int
    page: int
    page_size: int


class ContactCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    created_at: Optional[datetime] = None


class PipelineResponse(BaseModel):
    id: int
    name: str
    status: str
    stages: Optional[List[dict]] = None


class LeadResponse(BaseModel):
    id: int
    name: str
    price: Optional[int] = None
    status: str
    pipeline_id: Optional[int] = None
    created_at: Optional[datetime] = None


JSON_SCHEMAS = {
    "auth_login": {
        "type": "object",
        "required": ["access_token", "refresh_token"],
        "properties": {
            "access_token": {"type": "string"},
            "refresh_token": {"type": "string"},
            "expires_in": {"type": "integer"},
            "token_type": {"type": "string"},
        },
    },
    "auth_refresh": {
        "type": "object",
        "required": ["access_token"],
        "properties": {
            "access_token": {"type": "string"},
            "expires_in": {"type": "integer"},
            "token_type": {"type": "string"},
        },
    },
    "entity": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"},
        },
    },
    "contact": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "phone": {"type": "string"},
            "company": {"type": "string"},
        },
    },
    "error": {
        "type": "object",
        "required": ["error"],
        "properties": {
            "error": {"type": "string"},
            "message": {"type": "string"},
            "code": {"type": "integer"},
        },
    },
    "pagination": {
        "type": "object",
        "required": ["items", "total", "page", "page_size"],
        "properties": {
            "items": {"type": "array"},
            "total": {"type": "integer", "minimum": 0},
            "page": {"type": "integer", "minimum": 1},
            "page_size": {"type": "integer", "minimum": 1},
        },
    },
}


def validate(data: dict, schema_name: str) -> bool:
    schema = JSON_SCHEMAS.get(schema_name)
    if not schema:
        raise ValueError(f"Schema '{schema_name}' not found")
    try:
        jsonschema_validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False


def validate_response(response, schema_name: str) -> bool:
    try:
        data = response.json()
        return validate(data, schema_name)
    except Exception:
        return False


def validate_pydantic(data: dict, model_class) -> bool:
    try:
        model_class(**data)
        return True
    except Exception:
        return False