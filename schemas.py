import re
import bleach
import html
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, StrictStr, ConfigDict
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
    cleaned = bleach.clean(text, tags=[], attributes={}, strip=True)
    return html.unescape(cleaned)

class RegisterSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    username: StrictStr = Field(..., pattern=USERNAME_REGEX, min_length=3, max_length=30)
    email: EmailStr
    password: StrictStr = Field(..., min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)
    confirm_password: StrictStr
    full_name: Optional[StrictStr] = Field(default="", max_length=FULL_NAME_MAX)

    @field_validator('username')
    def validate_username(cls, v):
        if not isinstance(v, str):
            raise ValueError('username must be a string')
        return v.strip().lower()

    @field_validator('full_name')
    def validate_full_name(cls, v):
        if not isinstance(v, str):
            return ''
        return sanitize_html(v.strip())

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

class LoginSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    username: StrictStr = Field(..., min_length=1)
    password: StrictStr = Field(..., min_length=1)

    @field_validator('username')
    def validate_username(cls, v):
        if not isinstance(v, str):
            raise ValueError('username must be a string')
        return v.strip().lower()

class UpdateProfileSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    full_name: Optional[StrictStr] = Field(default=None, max_length=FULL_NAME_MAX)
    bio: Optional[StrictStr] = Field(default=None, max_length=500)
    avatar_url: Optional[StrictStr] = Field(default=None, max_length=500)
    birthday: Optional[StrictStr] = Field(default=None, max_length=100)
    status: Optional[StrictStr] = Field(default=None, max_length=100)

    @field_validator('full_name', 'bio', 'avatar_url', 'birthday', 'status', mode='before')
    def sanitize_fields(cls, v):
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError('must be a string')
        return sanitize_html(v.strip())

    @field_validator('avatar_url')
    def validate_avatar_url(cls, v):
        if not v:
            return v
        parsed = urlparse(v)
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
            raise ValueError('Avatar URL must be a valid http(s) URL')
        return v

class ProjectSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    title: StrictStr = Field(..., min_length=1, max_length=100)
    link: StrictStr = Field(..., min_length=1, max_length=500)
    description: StrictStr = Field(..., min_length=1, max_length=1000)

    @field_validator('title', 'description', mode='before')
    def sanitize_text_fields(cls, v):
        if v is None:
            return ''
        if not isinstance(v, str):
            raise ValueError('must be a string')
        return sanitize_html(v.strip())

    @field_validator('link', mode='before')
    def sanitize_link(cls, v):
        if v is None:
            return ''
        if not isinstance(v, str):
            raise ValueError('must be a string')
        return sanitize_html(v.strip())

    @field_validator('link')
    def validate_http_url(cls, v):
        parsed = urlparse(v)
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
            raise ValueError('Project link must be a valid http(s) URL')
        return v

class RoadmapSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    career_name: StrictStr = Field(..., min_length=1, max_length=150)
    course_name: StrictStr = Field(..., min_length=1, max_length=150)
    category: Optional[StrictStr] = Field(default='', max_length=100)
    roadmap_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('career_name', 'course_name', 'category', mode='before')
    def sanitize_roadmap_text(cls, v):
        if v is None:
            return ''
        if not isinstance(v, str):
            raise ValueError('must be a string')
        return sanitize_html(v.strip())

class RecommendationRequestSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    marks: float = Field(..., ge=0, le=100)
    # Fixed: Pydantic v2 uses max_items for List, not max_length
    skills: List[StrictStr] = Field(..., min_items=1, max_items=20)
    education_level: StrictStr = Field(default='SSLC', max_length=30)

    @field_validator('skills')
    def sanitize_skills(cls, v):
        cleaned = [sanitize_html(skill.strip()[:50]) for skill in v if isinstance(skill, str) and skill.strip()]
        if not cleaned:
            raise ValueError('Please select at least one skill')
        return cleaned

    @field_validator('education_level')
    def sanitize_education_level(cls, v):
        if not isinstance(v, str):
            return 'SSLC'
        return sanitize_html(v.strip()[:30]) or 'SSLC'

class AIQuestionRequestSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    category: StrictStr = Field(..., min_length=1, max_length=50)
    level: StrictStr = Field(default='beginner', max_length=20)
    count: int = Field(default=5, ge=1, le=50)
    role: Optional[StrictStr] = Field(default=None, max_length=100)
    topic: Optional[StrictStr] = Field(default=None, max_length=100)

    @field_validator('category', 'level', 'role', 'topic', mode='before')
    def sanitize_ai_text(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise TypeError('must be a string')
        return sanitize_html(v.strip())

    @field_validator('level')
    def normalize_level(cls, v):
        return v.lower()

class SkillTrackerCareerSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    career_name: StrictStr = Field(..., min_length=1, max_length=150)

    @field_validator('career_name', mode='before')
    def sanitize_career_name(cls, v):
        if not isinstance(v, str):
            raise ValueError('career_name must be a string')
        return sanitize_html(v.strip())


class SkillTrackerToggleSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    skill_key: StrictStr = Field(..., min_length=1, max_length=120)
    completed: bool

    @field_validator('skill_key', mode='before')
    def sanitize_skill_key(cls, v):
        if not isinstance(v, str):
            raise ValueError('skill_key must be a string')
        return sanitize_html(v.strip().lower())


class MockInterviewRequestSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    category: StrictStr = Field(..., min_length=1, max_length=50)
    level: StrictStr = Field(default='beginner', max_length=20)
    message: StrictStr = Field(..., min_length=1, max_length=1000)
    # Fixed: Pydantic v2 uses max_items for List, not max_length
    history: List[Dict[str, Any]] = Field(default_factory=list, max_items=30)
    # Number of interviewer questions already shown before the latest answer.
    # Older clients may omit it; the server will estimate progress from history.
    question_count: Optional[int] = Field(default=None, ge=0, le=30)

    @field_validator('category', 'level', 'message', mode='before')
    def sanitize_mock_text(cls, v):
        if v is None:
            return ''
        if not isinstance(v, str):
            raise TypeError('must be a string')
        return sanitize_html(v.strip())

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


class MockInterviewReportRequestSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    category: StrictStr = Field(..., min_length=1, max_length=50)
    level: StrictStr = Field(default='beginner', max_length=20)
    history: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50)

    @field_validator('category', 'level', mode='before')
    def sanitize_report_text(cls, v):
        if v is None:
            return ''
        if not isinstance(v, str):
            raise TypeError('must be a string')
        return sanitize_html(v.strip())

    @field_validator('level')
    def normalize_report_level(cls, v):
        return v.lower()

    @field_validator('history')
    def sanitize_report_history(cls, v):
        cleaned = []
        for item in v[:50]:
            if not isinstance(item, dict):
                continue
            role = str(item.get('role', '')).strip()
            content = sanitize_html(str(item.get('content', '')).strip()[:1000])
            if role in {'user', 'ai', 'model', 'assistant'} and content:
                cleaned.append({'role': role, 'content': content})
        return cleaned
