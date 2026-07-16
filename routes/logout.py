from fastapi.responses import RedirectResponse
from fastapi import APIRouter


logout_router = APIRouter()

@logout_router.get("/logout")
async def logout():

    response = RedirectResponse("/", status_code=303)

    response.delete_cookie("access_token")
    response.delete_cookie("session")
    response.delete_cookie("csrftoken")

    return response