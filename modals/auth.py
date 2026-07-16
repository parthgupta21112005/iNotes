from pydantic import BaseModel

class Auth(BaseModel):
    name: str
    email: str
    password: str
    confirmpassword: str

class User(BaseModel):
    name: str
    email: str | None = None
    disabled: bool | None = None

class Token(BaseModel):
    access_token: str
    token_type: str