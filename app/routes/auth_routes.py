from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter
from app.auth.jwt_handler import create_access_token
from fastapi import Depends


router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login")
async def login():
    """
    Basic login (no DB user yet).
    """
    token = create_access_token({"sub": "demo_user"})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    return {"message": "Authenticated"}