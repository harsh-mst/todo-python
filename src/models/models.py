from typing_extensions import Annotated
from pydantic import BaseModel, BeforeValidator, Field, EmailStr
from typing import Optional
from datetime import datetime


PyObjectId = Annotated[str, BeforeValidator(str)]


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: Annotated[EmailStr, Field(title="Enter your email", min_length=5)]
    password: Annotated[str, Field(title="Enter your password", min_length=5)]

    model_config = {
    "populate_by_name": True
}


class TasksModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: Annotated[str, Field(...,
                                title="Enter the title of the task", min_length=5)]
    description: Annotated[Optional[str], Field(
        title=" Enter the description of the task(optional)")]
    completed: bool = False
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.now())

    model_config = {
    "populate_by_name": True
}

