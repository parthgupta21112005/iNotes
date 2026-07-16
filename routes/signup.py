from fastapi import APIRouter, Request
from modals.auth import Auth
from schemas.auth import authEntity
from config.db import collection2, templates, SECRET_KEY, ALGORITHM
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
import jwt
from jwt.exceptions import InvalidTokenError
from routes.signin import create_access_token

# Security module
from pwdlib import PasswordHash
pwd_context = PasswordHash.recommended()


signup = APIRouter()

@signup.get("/", response_class=HTMLResponse)
async def root_redirect():
    return RedirectResponse(url="/sign-up", status_code=303)

@signup.get("/sign-up", response_class=HTMLResponse)
async def signup_page(request: Request):
    token = request.cookies.get("access_token")

    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # User already logged in
            return RedirectResponse("/notes", status_code=303)

        except InvalidTokenError:
            pass
    response= templates.TemplateResponse(
        request=request, name="sign-up.html", context={"page": "sign-up"}
    )
    response.headers["Cache-Control"] = "no-store"
    return response



@signup.post("/sign-up")
async def auth_person(request: Request):
    form = await request.form()
    form_dict = dict(form)

    user = Auth(**form_dict)

    if user.password != user.confirmpassword:
        return {"error": "Passwords do not match"}
    
    hashed_password = pwd_context.hash(user.password)
    result = collection2.insert_one({
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    })
    new_user = collection2.find_one({"_id": result.inserted_id})
    response = RedirectResponse(url="/notes", status_code=303)
    access_token = create_access_token(data={"sub": user.email})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response
    