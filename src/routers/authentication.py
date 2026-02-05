from fastapi import APIRouter, HTTPException, status, Depends
from ..schemas.schemas import RegisterLoginUser, Token, UpdatePassword
from ..models import UserModel
from ..db import collections
from ..utils.hashing import password_hash, verify_password
from ..utils.token import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from ..utils.oauth2 import get_current_user
from pymongo import ReturnDocument


router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=UserModel)
async def register_user(request: RegisterLoginUser):

    existing_user = await collections.users_collection.find_one(
        {"email": request.email}
    )

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")

    new_user = request.model_dump(by_alias=True, exclude=["id"])

    hashed_password = password_hash.hash(request.password)
    new_user["password"] = hashed_password

    result = await collections.users_collection.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)

    return new_user


@router.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends()):

    user = await collections.users_collection.find_one({"email": request.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User dosen't exist")

    check_password = verify_password(request.password, user["password"])
    if not check_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user["email"]}
    )
    return {
        # "_id": user["_id"],
        # "email": user["email"],
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/update-password")
async def update_password(request: UpdatePassword, currentUser: UserModel = Depends(get_current_user)):
    check_password = verify_password(
        request.currentPassword, currentUser.password)
    if not check_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    hash_password = password_hash.hash(request.newPassword)

    update_user = await collections.users_collection.find_one_and_update(
        {"email": currentUser.email},
        {"$set": {"password": hash_password}},
        return_document=ReturnDocument.AFTER
    )

    if not update_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "Password changed succesfully"}


@router.delete("/delete-account")
async def delete_account(currentUser: UserModel = Depends(get_current_user)):
    result = await collections.users_collection.delete_one({
        "email": currentUser.email
    })

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized request")

    return {"message": "User deleted successfully"}
