import re
import bleach
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional

# Constants matching config.py
USERNAME_REGEX = r'^[a-zA-Z0-9_]{3,30}$'
PASSWORD_MIN = 6
PASSWORD_MAX = 128
FULL_NAME_MAX = 100

def sanitize_html(text: str) -> str:
    """Sanitize HTML tags using Bleach to prevent XSS."""
    if not text:
        return text
    # Strip all HTML tags
    return bleach.clean(text, tags=[], attributes={}, strip=True)

class RegisterSchema(BaseModel):
    username: str = Field(..., pattern=USERNAME_REGEX, min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)
    confirm_password: str
    full_name: Optional[str] = Field(default="", max_length=FULL_NAME_MAX)

    @field_validator('username')
    def validate_username(cls, v):
        return v.strip().lower()

    @field_validator('full_name')
    def validate_full_name(cls, v):
        return sanitize_html(v.strip())

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

class LoginSchema(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

    @field_validator('username')
    def validate_username(cls, v):
        return v.strip().lower()

class UpdateProfileSchema(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=FULL_NAME_MAX)
    bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    birthday: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default=None, max_length=100)

    @field_validator('full_name', 'bio', 'avatar_url', 'birthday', 'status', mode='before')
    def sanitize_fields(cls, v):
        if v is not None:
            return sanitize_html(str(v).strip())
        return v
