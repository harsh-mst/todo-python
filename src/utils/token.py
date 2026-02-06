from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from ..schemas.schemas import TokenData
from ..db import collections
from ..models import UserModel
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        # token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception

    user = await collections.users_collection.find_one(
        {"email": email}
    )

    if user is None:
        raise credentials_exception

    user["_id"] = str(user["_id"])
    return UserModel(**user)
