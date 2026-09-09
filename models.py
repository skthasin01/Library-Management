from database import Base
from sqlalchemy import Column, Integer,String,Boolean,Float,DateTime,ForeignKey
from datetime import datetime


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True)
    username = Column(String,unique=True)
    firstname = Column(String)
    lastname = Column(String)
    hash_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String) #librarian or member


class Books(Base):
    __tablename__ = 'books'

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    author = Column(String)
    category = Column(String)
    discription = Column(String)
    price = Column(Float,default=0.00)
    total_copies = Column(Integer,default=5)
    available_copies = Column(Integer,default=3)
    cover_image = Column(String,nullable=True)
    created_at = Column(DateTime,default=datetime.now)


class Reservations(Base):
    __tablename__ = 'reservations'

    id = Column(Integer,primary_key=True,index=True)
    book_id = Column(Integer,ForeignKey('books.id'))
    user_id = Column(Integer,ForeignKey('users.id'))
    reservation_date = Column(DateTime,default=datetime.now)
    status = Column(String,default='pending')
