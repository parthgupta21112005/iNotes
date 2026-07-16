import os
from dotenv import load_dotenv

load_dotenv()

from pymongo import MongoClient
from fastapi.templating import Jinja2Templates

client = MongoClient(os.getenv("MONGOURI"))
db = client["Fastapi_connection"] 
collection = db["fastapi_notes"]


db2 = client["authentication"] 
collection2 = db2["auth"]

templates = Jinja2Templates(directory="templates")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
