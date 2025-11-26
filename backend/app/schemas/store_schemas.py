from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class StoreBase(BaseModel):
    """Base schema for Store"""
    display_name: str = Field(..., min_length=1, max_length=100, description="User-facing name of the store")
    
    @field_validator('display_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and sanitize store name to prevent SQL injection"""
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check if name is not empty after stripping
        if not v:
            raise ValueError("Store name cannot be empty")
        
        # Only allow alphanumeric characters, spaces, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+$', v):
            raise ValueError("Store name can only contain letters, numbers, spaces, hyphens, and underscores")
        
        return v


class StoreCreate(StoreBase):
    """Schema for creating a new store"""
    pass


class StoreResponse(StoreBase):
    """Schema for store response"""
    id: int
    google_store_name: str  # Google FileSearchStore resource name
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class StoreListResponse(BaseModel):
    """Schema for list of stores"""
    stores: list[StoreResponse]
    total: int


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None
