from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from typing import Optional
from app.core.security import pwd_context
from app.auth.jwt_handler import create_access_token
from app.schemas.auth import UserLogin
from app.db.dependencies import get_db
from app.models.user import User
from sqlalchemy.future import select
from app.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(credentials: UserLogin, db=Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == credentials.username))
    user = result.scalars().first()

    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Successfully authenticated as {current_user.username}",
        "username": current_user.username,
        "role": current_user.role
    }


