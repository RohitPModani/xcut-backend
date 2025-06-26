from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
import re
from enum import Enum

class URLBase(BaseModel):
    target_url: str = Field(..., description="The target URL to be shortened")

    @field_validator('target_url')
    def validate_url(cls, v):
        if re.match(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$', v):
            return f'https://{v}'
        
        url_pattern = re.compile(
            r'^(https?://)?'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(v):
            raise ValueError('Invalid URL format')
        
        if not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        
        return v

class URLResponse(BaseModel):
    short_url: str
    target_url: str
    visits: int = 0
    created_at: datetime
    is_active: bool = True