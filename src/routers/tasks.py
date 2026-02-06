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
    new_task = {
        "title": request.title,
        "description": request.description,
        "user_id": ObjectId(currentUser.id),
        "completed": False,
        "created_at": datetime.utcnow()
    }

   
    result = await collections.tasks_collection.insert_one(new_task)

    response_task = {
        "id": str(result.inserted_id),
        "title": new_task["title"],
        "description": new_task["description"],
        "completed": new_task["completed"],
        "user_id": str(new_task["user_id"]),
        "created_at": new_task["created_at"]
    }

  
    return response_task


@router.get("/tasks", response_model=list[TaskResponse])
async def get_user_tasks(
    currentUser: UserModel = Depends(get_current_user)
):
    cursor = collections.tasks_collection.find(
        {"user_id": ObjectId(currentUser.id)}
    )
    tasks = await cursor.to_list(length=100)

   

    formatted_tasks = []
    for task in tasks:
        formatted_task = {
            "id": str(task["_id"]),
            "title": task.get("title", ""),
            "description": task.get("description", ""),
            "completed": task.get("completed", False),
            "user_id": str(task.get("user_id", "")),
            "created_at": task.get("created_at", datetime.utcnow())
        }
        formatted_tasks.append(formatted_task)



    return formatted_tasks


@router.get("/task/{task_id}", response_model=TaskResponse)
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

   
    formatted_task = {
        "id": str(task["_id"]),
        "title": task.get("title", ""),
        "description": task.get("description", ""),
        "completed": task.get("completed", False),
        "user_id": str(task.get("user_id", "")),
        "created_at": task.get("created_at", datetime.utcnow())
    }

    return formatted_task


@router.post("/update-task/{task_id}", response_model=TaskResponse)
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

    formatted_task = {
        "id": str(result["_id"]),
        "title": result.get("title", ""),
        "description": result.get("description", ""),
        "completed": result.get("completed", False),
        "user_id": str(result.get("user_id", "")),
        "created_at": result.get("created_at", datetime.utcnow())
    }

    return formatted_task


@router.post("/task-completed/{task_id}", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: str,
    currentUser: UserModel = Depends(get_current_user)
):
    task = await collections.tasks_collection.find_one(
        {
            "_id": ObjectId(task_id),
            "user_id": ObjectId(currentUser.id)
        }
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found or unauthorized"
        )

    new_status = not task.get("completed", False)

    result = await collections.tasks_collection.find_one_and_update(
        {
            "_id": ObjectId(task_id),
            "user_id": ObjectId(currentUser.id)
        },
        {"$set": {"completed": new_status}},
        return_document=ReturnDocument.AFTER
    )

    formatted_task = {
        "id": str(result["_id"]),
        "title": result.get("title", ""),
        "description": result.get("description", ""),
        "completed": result.get("completed", False),
        "user_id": str(result.get("user_id", "")),
        "created_at": result.get("created_at", datetime.utcnow())
    }

    return formatted_task


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
