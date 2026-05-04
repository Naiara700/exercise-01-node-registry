"""
Pydantic schemas for request/response validation.

NodeCreate: for POST body (name, host, port — all required)
NodeUpdate: for PUT body (host, port — optional)
NodeResponse: for API responses (includes id, status, timestamps)
"""

# TODO: Implement your Pydantic schemas here

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
 
 
class NodeCreate(BaseModel):
    name: str
    host: str
    port: int
 
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v
 
    @field_validator("host")
    @classmethod
    def host_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("host must not be empty")
        return v
 
    @field_validator("port")
    @classmethod
    def port_in_range(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v
 
 
class NodeUpdate(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
 
    @field_validator("host")
    @classmethod
    def host_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("host must not be empty")
        return v
 
    @field_validator("port")
    @classmethod
    def port_in_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v
 
 
class NodeResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
