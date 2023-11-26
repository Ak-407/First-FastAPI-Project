from fastapi import FastAPI, Form, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.db import new_users_collection, notes_collection
from fastapi import Depends
from bson import ObjectId
import hashlib

app = FastAPI()
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCredentials(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    username: str
    hashed_password: str
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(data: dict):
    return jwt.encode(data, "wTh5Cxa+jGl5bvTX9LzODIZwoRlWpctr8bYADg4a", algorithm="HS256")

def decode_jwt_token(token: str):
    return jwt.decode(token, "wTh5Cxa+jGl5bvTX9LzODIZwoRlWpctr8bYADg4a", algorithms=["HS256"])

def fake_hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(db, username: str):
    user_data = new_users_collection.find_one({"username": username})
    return user_data

# Use this dependency to get the current user based on the JWT token
async def get_current_user(token: str = Depends(decode_jwt_token)):
    return token

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})



# @app.get("/index", response_class=HTMLResponse)
# async def read_item(request: Request, token: str = Depends(get_current_user)):
#     docs = notes_collection.find({})
#     newDocs = []
#
#     for doc in docs:
#         title = doc.get("title", "No Title")
#         desc = doc.get("desc", "No Description")
#
#         newDocs.append({
#             "id": doc["_id"],
#             "title": title,
#             "desc": desc,
#         })
#
#     return templates.TemplateResponse("index.html", {"request": request, "newDocs": newDocs})
#



@app.get("/index", response_class=HTMLResponse)
async def read_item(request: Request):
    docs = notes_collection.find({})
    newDocs = []

    for doc in docs:
        title = doc.get("title")
        desc = doc.get("desc")

        newDocs.append({
            "id": doc["_id"],
            "title": title,
            "desc": desc,
        })

    return templates.TemplateResponse("index.html", {"request": request, "newDocs": newDocs})

@app.post("/index")
async def create_item(request: Request):
    form = await request.form()
    note_data = dict(form)
    notes_collection.insert_one(note_data)
    return {"Success": True}


@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})



# @app.post("/register")
# async def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
#     hashed_password = fake_hash_password(password)
#
#     if conn.jsamaan.newUsers.find_one({"username": username}):
#         return {"error": "Username already taken"}
#
#     conn.jsamaan.newUsers.insert_one({
#         "username": username,
#         "hashed_password": hashed_password,
#     })
#
#     return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

from fastapi.responses import RedirectResponse

# @app.post("/login")
# async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
#     user_data = get_user(conn, username)
#
#     if user_data and user_data.get("hashed_password") == fake_hash_password(password):
#         return RedirectResponse(url="/index")
#
#     raise HTTPException(status_code=401, detail="Invalid username or password")
#



@app.post("/register")
async def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    hashed_password = hash_password(password)

    if new_users_collection.find_one({"username": username}):
        return {"error": "Username already taken"}

    new_users_collection.insert_one({
        "username": username,
        "hashed_password": hashed_password,
    })

    return RedirectResponse(url="/login")

@app.post("/login")
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    user_data = get_user(new_users_collection, username)

    if user_data and verify_password(password, user_data.get("hashed_password")):
        # Create a JWT token on successful login
        token_data = {"sub": username}
        token = create_jwt_token(token_data)
        return RedirectResponse(url="/index", headers={"Authorization": f"Bearer {token}"})

    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/delete/{note_id}")
async def delete_item(note_id: str):
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count == 1:
        return RedirectResponse(url="/index")
    else:
        raise HTTPException(status_code=404, detail="Note not found")
