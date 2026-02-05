from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from typing_extensions import Annotated
from typing import Optional
from datetime import datetime


PyObjectId = Annotated[str, BeforeValidator(str)]


class RegisterLoginUser(BaseModel):
    email: Annotated[EmailStr, Field(
        title="Enter your username", min_length=5)]
    password: Annotated[str, Field(title="Enter your password", min_length=5)]


class CreateTask(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: Annotated[str, Field(...,
                                title="Enter the title of the task", min_length=5)]
    description: Annotated[Optional[str], Field(
        title=" Enter the description of the task(optional)")]
    completed: bool = False
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.now())


class CreateTaskRequest(BaseModel):
    title: Annotated[str, Field(
        ..., title="Enter the title of the task", min_length=5
    )]
    description: Annotated[Optional[str], Field(
        title="Enter the description of the task (optional)"
    )] = None

class TaskResponse(BaseModel):
    id: PyObjectId
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime


class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: bool = None

class UpdatePassword(BaseModel):
    currentPassword: str
    newPassword: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
