from datetime import datetime, timedelta
from faulthandler import disable
from subprocess import IDLE_PRIORITY_CLASS
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from passlib.context import CryptContext

from pydantic import BaseModel
from db import session
from model import User_DB,UserTable,User_Test

# 템플릿 함수
from fastapi.templating import Jinja2Templates #템플릿 추가
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "49db04f6b4fceab699510b7b8af08b2fed445d03cb77a914bd27aebad7402ace"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None





class UserInDB(User_Test):
    hashed_password: str



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_password(plain_password, hashed_password):  
    return pwd_context.verify(plain_password, hashed_password)

def verify_password_DB(plain_password, hashed_password): 
    print(plain_password)
    print(hashed_password) 
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):

    return pwd_context.hash(password)



def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def get_user_DB(username: str):
    user = session.query(UserTable).filter(UserTable.name == username).first()
    print(user)

#    test =UserTable(username=user.username,email=user.email,full_name=user.full_name,disabled=user.disabled,hashed_password=user.hashed_password)
    print("비밀번호 PWD")
    print(get_password_hash(user.pwd))
    test =UserTable(id=user.id,pwd=user.pwd,hashed_password=user.hashed_password)

    return test


def authenticate_user(fake_db, username: str, password: str):  
    user_db = get_user_DB(username)
    if not user_db:
        return False

    if not verify_password_DB(password, user_db.hashed_password):
        return False
    
    return user_db



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    print("token")
    print(token)
    print(oauth2_scheme)
    print("---------------")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    #user = get_user(fake_users_db, username=token_data.username)
    user = get_user_DB( username=token_data.username)
    
    print(type(user))
    print(user)

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User_Test = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print("hello")
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User_Test)
async def read_users_me(current_user: User_Test = Depends(get_current_active_user)):
    
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User_Test = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.id}]

app.mount("/templates", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def get(request: Request):

    context = {}
    context['request'] = request
    return templates.TemplateResponse("main.html",context)


# ----------API 정의------------

# ----------API 정의------------
@app.get("/users", response_class=HTMLResponse)
async def read_users(request: Request):
    print("read_users >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    context = {}

    users = session.query(UserTable).all()

    context['request'] = request
    context['users'] = users

    return templates.TemplateResponse("user_list.html", context)


@app.get("/users/{user_id}", response_class=HTMLResponse)
async def read_user(request: Request, user_id: int):
    print("read_user >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    context = {}

    user = session.query(UserTable).filter(UserTable.id == user_id).first()
    print(user.name)
    context['name'] = user.name
    context['age'] = user.age
    context['request'] = request

    return templates.TemplateResponse("user_detail.html", context)


@app.post("/users")
async def create_user(users: User_Test):
    print("create_user >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    # data = await request.json()
    list_user = list(users)
    print(list_user[1][1])

 
    user = authenticate_user(fake_users_db, list_user[1][1], list_user[2][1])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    print("==============생성된 토큰================")
    print(access_token)
    print("========================================")
    return { 'result_msg Registered...' }


@app.put("/users")
async def modify_users(users: User_Test):
    print("modify_user >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    return { 'result_msg': f"updated..." }


@app.delete("/users")
async def delete_users(users: User_Test):
    print("delete_user >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    return {'result_msg': f"User deleted..."}