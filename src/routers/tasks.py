from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.schemas import CreateTask, CreateTaskRequest, TaskResponse, UpdateTask
from ..models import UserModel, TasksModel
from ..utils.oauth2 import get_current_user
from ..db import collections
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument

router = APIRouter(tags=["Tasks"])


@router.post("/create-task", response_model=TaskResponse)
async def createTask(
    request: CreateTaskRequest,
    currentUser: UserModel = Depends(get_current_user)
):
    new_task = request.model_dump(by_alias=True, exclude=["id"])
    new_task["user_id"] = ObjectId(currentUser.id)
    new_task["completed"] = False
    new_task["created_at"] = datetime.utcnow()

    result = await collections.tasks_collection.insert_one(new_task)
    new_task["id"] = str(result.inserted_id)
    return new_task


@router.get("/tasks", response_model=list[TasksModel])
async def get_user_tasks(
    currentUser: UserModel = Depends(get_current_user)
):
    all_tasks = collections.tasks_collection.find(
        {"user_id": ObjectId(currentUser.id)}
    )
    return await all_tasks.to_list(length=100)


@router.get("/task/{task_id}", response_model=TasksModel)
async def get_task(
    task_id: str,
    currentUser: UserModel = Depends(get_current_user)
):
    task = await collections.tasks_collection.find_one({
        "_id": ObjectId(task_id),
        "user_id": ObjectId(currentUser.id)
    })

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.post("/update-task/{task_id}", response_model=TasksModel)
async def update_task(
    task_id: str,
    request: UpdateTask,
    currentUser: UserModel = Depends(get_current_user)
):
    update_data = {
        k: v for k, v in request.model_dump().items() if v is not None
    }

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided to update"
        )

    result = await collections.tasks_collection.find_one_and_update(
        {
            "_id": ObjectId(task_id),
            "user_id": ObjectId(currentUser.id)
        },
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return result


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    currentUser: UserModel = Depends(get_current_user)
):
    result = await collections.tasks_collection.delete_one({
        "_id": ObjectId(task_id),
        "user_id": ObjectId(currentUser.id)
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    return {"message": "Task deleted successfully"}
