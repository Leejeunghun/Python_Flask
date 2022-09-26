
from datetime import datetime
from enum import IntEnum
from sqlite3 import Date, Timestamp, connect
import string
from winreg import EnumKey
from sqlalchemy import Column,Integer,String,DateTime,Text,Enum,SmallInteger,Float,Boolean
from pydantic import BaseModel
from db import Base
from db import ENGINE
from typing import Optional



class User_DB(Base):
    __tablename__ = 'usera'
    Sample_pk = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String(255))
    full_name = Column(String(255))
    email = Column(String(255))
    hashed_password = Column(String(255))
    disabled = Column(Boolean)


class UserTable(Base):
    __tablename__ = 'user'
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(255))
    pwd = Column(String(255))
    hashed_password = Column(String(255))


class User_Test(BaseModel):
    id   : int
    name : str
    pwd  : str
    disabled: Optional[bool] = None
