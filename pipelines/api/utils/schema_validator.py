import jsonschema
from jsonschema import validate as jsonschema_validate, ValidationError
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class AmoCRMAccount(BaseModel):
    id: int
    name: str
    subdomain: Optional[str] = None
    currency: Optional[str] = "RUB"
    timezone: Optional[str] = "Europe/Moscow"


class AmoCRMContact(BaseModel):
    id: int
    name: str
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    custom_fields_values: Optional[List[dict]] = None
    _embedded: Optional[dict] = None


class AmoCRMCompany(BaseModel):
    id: int
    name: str
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class AmoCRMLead(BaseModel):
    id: int
    name: str
    price: Optional[int] = 0
    status_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class AmoCRMTask(BaseModel):
    id: int
    name: str
    task_type_id: int
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    complete_till: Optional[int] = None


class AmoCRMUser(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    is_admin: Optional[bool] = False
    is_active: Optional[bool] = True


class AmoCRMPipeline(BaseModel):
    id: int
    name: str
    sort: int = 0
    is_default: bool = False


class AmoCRMError(BaseModel):
    error: str
    error_code: Optional[str] = None
    validation_errors: Optional[List[dict]] = None


JSON_SCHEMAS = {
    "contact": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "created_at": {"type": "integer"},
            "updated_at": {"type": "integer"},
        },
    },
    "company": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "created_at": {"type": "integer"},
            "updated_at": {"type": "integer"},
        },
    },
    "lead": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "price": {"type": "integer"},
            "status_id": {"type": "integer"},
            "pipeline_id": {"type": "integer"},
            "created_at": {"type": "integer"},
            "updated_at": {"type": "integer"},
        },
    },
    "task": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "task_type_id": {"type": "integer"},
            "entity_type": {"type": "string"},
            "entity_id": {"type": "integer"},
        },
    },
    "user": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "is_admin": {"type": "boolean"},
            "is_active": {"type": "boolean"},
        },
    },
    "pipeline": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "sort": {"type": "integer"},
            "is_default": {"type": "boolean"},
        },
    },
    "error": {
        "type": "object",
        "required": ["error"],
        "properties": {
            "error": {"type": "string"},
            "error_code": {"type": "string"},
            "validation_errors": {"type": "array"},
        },
    },
    "embedded": {
        "type": "object",
        "required": ["contacts"],
        "properties": {
            "contacts": {"type": "array"},
            "companies": {"type": "array"},
            "leads": {"type": "array"},
            "tasks": {"type": "array"},
        },
    },
    "pagination": {
        "type": "object",
        "required": ["_embedded"],
        "properties": {
            "_embedded": {"type": "object"},
            " pagination": {"type": "object"},
            "page": {"type": "integer", "minimum": 1},
            "limit": {"type": "integer", "minimum": 1},
            "total": {"type": "integer", "minimum": 0},
        },
    },
}


def validate(data: dict, schema_name: str) -> bool:
    schema = JSON_SCHEMAS.get(schema_name)
    if not schema:
        return True
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