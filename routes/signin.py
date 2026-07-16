from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from config.db import collection2, templates, SECRET_KEY, ALGORITHM
from modals.auth import User
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.responses import RedirectResponse

signin = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database me se data lana
def database_data(newdocs):
    docs = collection2.find({})
    for doc in docs:
        newdocs.append({
            "_id": doc['_id'],
            "name": doc['name'],
            "email": doc['email'],
            "hashed_password": doc['password'],
            "disabled": False
        })
    return newdocs
newdocs=[]
db_data = database_data(newdocs)

class UserInDB(User):
    hashed_password: str

password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(db_data, email: str):
    for db in db_data:
        if email == db["email"]:
            user_dict = {
                "name": db['name'],
                "email": db['email'],
                "hashed_password": db['hashed_password'],
                "disabled": db['disabled']
            }
            return UserInDB(**user_dict)
    return None
    
def authenticate_user(db_data, email: str, password: str):
    user = get_user(db_data, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db_data, username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@signin.get("/sign-in", response_class=HTMLResponse)
async def signin_page(request: Request):
    token = request.cookies.get("access_token")

    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # User already logged in
            return RedirectResponse("/notes", status_code=303)

        except InvalidTokenError:
            pass
    response= templates.TemplateResponse(
        request=request, name="sign-in.html", context={"page": "sign-in"}
    )
    response.headers["Cache-Control"] = "no-store"
    return response

@signin.post("/token")
async def login_for_access_token(request: Request):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    user = authenticate_user(db_data, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/notes", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response
