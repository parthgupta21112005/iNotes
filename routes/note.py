from fastapi import APIRouter, Request, Depends, HTTPException
from modals.note import Note
from config.db import collection, templates, SECRET_KEY, ALGORITHM
from schemas.note import noteEntity, notesEntity
from fastapi.responses import HTMLResponse
from routes.signin import get_current_user
from fastapi.responses import RedirectResponse
import jwt
from jwt.exceptions import InvalidTokenError
# main
note = APIRouter()

def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@note.get("/notes", response_class=HTMLResponse)
async def read_item(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/sign-in", status_code=303)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return RedirectResponse(url="/sign-in", status_code=303)
    except InvalidTokenError:
        return RedirectResponse(url="/sign-in", status_code=303)
    docs = collection.find({"owner_email": email})
    newdocs=[]
    for doc in docs:
        newdocs.append({
            "_id": str(doc['_id']),
            "title": doc['title'],
            "desc": doc['desc'],
            "important": doc['important']
        })
    return templates.TemplateResponse(
        request=request, name="index.html", context={"newdocs": newdocs, "user": email, "page": "notes"}
    )

@note.post("/notes")
async def create_item(request: Request):
    email = get_current_user_from_cookie(request)
    form = await request.form()
    formDict=dict(form)
    formDict['important']=True if formDict.get('important')=="on" else False
    formDict['owner_email'] = email
    collection.insert_one(dict(formDict))
    return RedirectResponse(url="/notes", status_code=303)
