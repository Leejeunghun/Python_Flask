
from datetime import datetime
from sqlite3 import Date, Timestamp, connect
import string
from winreg import EnumKey
from sqlalchemy import Column,Integer,String,DateTime,Text,Enum,SmallInteger,Float
from pydantic import BaseModel
from db import Base
from db import ENGINE



class User_DB(Base):
    __tablename__ = 'user'
    Sample_pk = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String(255))
    full_name = Column(String(255))
    email = Column(String(255))
    hashed_password = Column(String(255))
    disabled = Column(Integer)
