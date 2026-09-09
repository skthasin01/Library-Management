from fastapi import FastAPI,APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
from models import Users,Books,Reservations
from database import Sessionlocal
from typing import Annotated,Optional
from fastapi.responses import JSONResponse
from datetime import timedelta,datetime,timezone

from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from router.auth import get_current_user

router = APIRouter()

class CreateBooks(BaseModel):
    title : str = Field
    author : str
    category : str
    discription : str = Field(default="",max_length=200)
    price : float = Field(default=0.0,ge=0)
    total_copies : int = Field(default=1)

class UpdateBooks(BaseModel):
    title : Optional[str] = Field(default=None)
    author : Optional[str] = Field(default=None)
    category : Optional[str] = Field(default=None)
    discription : Optional[str] = Field(default=None)
    price : Optional[float] = Field(default=None)
    total_copies : Optional[int] = Field(default=None)
    available_copies : Optional[int] = Field(default=None)

def get_db():
    db = Sessionlocal()
    try:
        yield db 
    finally:
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post('/admin/create_book')
def create_book(user:user_dependency,db : db_dependency,newbook : CreateBooks):

    if user is None or user.get('role') != 'librarian':
        raise HTTPException(status_code=401, detail='Faild Authentication')

    book_model = Books(
        **newbook.model_dump(),
        available_copies = newbook.total_copies
    )

    db.add(book_model)
    db.commit()

    return JSONResponse(status_code=201,content={'message': 'Book added Successfully'})

@router.put('/admin/update_book/{book_id}')
def create_book(user:user_dependency,db : db_dependency,updatebook : UpdateBooks,book_id : int):

    if user is None or user.get('role') != 'librarian':
        raise HTTPException(status_code=401, detail='Faild Authentication')

    book = db.query(Books).filter(Books.id == book_id).firts()
    if book is None:
        raise HTTPException(status_code=404, detail='Book not Found!!')
    
    update_book_data = updatebook.model_dump(exclude_unset=True)

    for key,value in update_book_data.item():
        setattr(book,key,value)

    db.commit()

    return JSONResponse(status_code=200,content={'message': 'Book Updated Successfully'})

@router.delete('/admin/delete_book/{book_id}')
def delete_book(user:user_dependency,db : db_dependency,book_id : int):

    if user is None or user.get('role') != 'librarian':
        raise HTTPException(status_code=401, detail='Faild Authentication')

    book = db.query(Books).filter(Books.id == book_id).firts()
    if book is None:
        raise HTTPException(status_code=404, detail='Book not Found!!')
    
    db.query(Books).filter(Books.id == book_id).delete()
    db.commit()

    return JSONResponse(status_code=200,content={'message': 'Book Deleted Successfully'})