import re
import bleach
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

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

    @field_validator('avatar_url')
    def validate_avatar_url(cls, v):
        if not v:
            return v
        parsed = urlparse(v)
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
            raise ValueError('Avatar URL must be a valid http(s) URL')
        return v

class ProjectSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    link: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1, max_length=1000)

    @field_validator('title', 'description', mode='before')
    def sanitize_text_fields(cls, v):
        return sanitize_html(str(v).strip()) if v is not None else ''

    @field_validator('link', mode='before')
    def sanitize_link(cls, v):
        return sanitize_html(str(v).strip()) if v is not None else ''

    @field_validator('link')
    def validate_http_url(cls, v):
        parsed = urlparse(v)
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
            raise ValueError('Project link must be a valid http(s) URL')
        return v

class RoadmapSchema(BaseModel):
    career_name: str = Field(..., min_length=1, max_length=150)
    course_name: str = Field(..., min_length=1, max_length=150)
    category: Optional[str] = Field(default='', max_length=100)
    roadmap_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('career_name', 'course_name', 'category', mode='before')
    def sanitize_roadmap_text(cls, v):
        return sanitize_html(str(v).strip()) if v is not None else ''

class RecommendationRequestSchema(BaseModel):
    marks: float = Field(..., ge=0, le=100)
    skills: List[str] = Field(..., min_length=1, max_length=20)
    education_level: str = Field(default='SSLC', max_length=30)

    @field_validator('skills')
    def sanitize_skills(cls, v):
        cleaned = [sanitize_html(str(skill).strip()[:50]) for skill in v if str(skill).strip()]
        if not cleaned:
            raise ValueError('Please select at least one skill')
        return cleaned

    @field_validator('education_level')
    def sanitize_education_level(cls, v):
        return sanitize_html(str(v).strip()[:30]) or 'SSLC'

class AIQuestionRequestSchema(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    level: str = Field(default='beginner', max_length=20)
    count: int = Field(default=5, ge=1, le=50)
    role: Optional[str] = Field(default=None, max_length=100)
    topic: Optional[str] = Field(default=None, max_length=100)

    @field_validator('category', 'level', 'role', 'topic', mode='before')
    def sanitize_ai_text(cls, v):
        if v is None:
            return None
        return sanitize_html(str(v).strip())

    @field_validator('level')
    def normalize_level(cls, v):
        return v.lower()

class MockInterviewRequestSchema(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    level: str = Field(default='beginner', max_length=20)
    message: str = Field(..., min_length=1, max_length=1000)
    history: List[Dict[str, Any]] = Field(default_factory=list, max_length=30)

    @field_validator('category', 'level', 'message', mode='before')
    def sanitize_mock_text(cls, v):
        return sanitize_html(str(v).strip()) if v is not None else ''

    @field_validator('level')
    def normalize_mock_level(cls, v):
        return v.lower()

    @field_validator('history')
    def sanitize_history(cls, v):
        cleaned = []
        for item in v[:30]:
            if not isinstance(item, dict):
                continue
            role = str(item.get('role', '')).strip()
            content = sanitize_html(str(item.get('content', '')).strip()[:1000])
            if role in {'user', 'ai', 'model', 'assistant'} and content:
                cleaned.append({'role': role, 'content': content})
        return cleaned
