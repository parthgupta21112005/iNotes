from fastapi import FastAPI
from routes.note import note
from routes.signup import signup
from routes.signin import signin
from routes.logout import logout_router


app=FastAPI()


# Authentication router ko root par rakho
app.include_router(signup, prefix="", tags=["Authentication"])
app.include_router(signin, prefix="", tags=["Authentication"])
app.include_router(logout_router, prefix="", tags=["Authentication"])

# Notes router ko alag prefix par rakho
app.include_router(note, prefix="", tags=["Notes"])