from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Project Schemas ---
class ProjectCreate(BaseModel):
    title: str

class ProjectUpdate(BaseModel):
    chat_history: Optional[List[str]] = None
    ui_tree: Optional[Dict[str, Any]] = None
    files_json: Optional[Dict[str, str]] = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    user_id: int
    chat_history: str # Serialized JSON string
    ui_tree: str # Serialized JSON string
    files_json: str # Serialized JSON string
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
