from fastapi import FastAPI,Depends,HTTPException,Query
from sqlalchemy.orm import Session
from typing import Annotated,Optional
import models
from models import Books,Users,Reservations,IssueRecords
from database import engine,Sessionlocal
from fastapi.responses import JSONResponse
from router import admin,auth
from router.auth import get_current_user

app = FastAPI()

models.Base.metadata.create_all(bind = engine)
app.include_router(auth.router)
app.include_router(admin.router)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

@app.get('/books/all')
def get_all_books(user : user_dependency,db:db_dependency):

    if user is None:
        raise HTTPException(status_code=401,detail="Faild Authentication")
    books = db.query(Books).all()
    return books

@app.get('/books/{book_id}')
def get_specific_books(user : user_dependency,db:db_dependency,book_id : int):

    if user is None:
        raise HTTPException(status_code=401,detail="Faild Authentication")
    book = db.query(Books).filter(Books.id == book_id).first()

    if book in None :
        raise HTTPException(status_code=404,detail='Book not found!!')

    return book

@app.post('/reserve/{book_id}')
def reserve_book(user : user_dependency,db:db_dependency,book_id : int):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild Authentication")

    book = db.query(Books).filter(Books.id == book_id).first()
    if book in None :
        raise HTTPException(status_code=404,detail='Book not found!!')

    reservation_model = Reservations(
        book_id = book_id,
        user_id = user.get('id'),
        status = 'pending'
    )
    db.add(reservation_model)
    db.commit()
    return JSONResponse(status_code=201,content={'message': 'Book Reserved Successfully'})

@app.delete('/reserve/cancel/{reservation_id}')
def cancel_reservation(user : user_dependency,db:db_dependency,reservation_id : int):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild Authentication")

    reservation = db.query(Reservations).filter(Reservations.id == reservation_id).first()
    if reservation in None :
        raise HTTPException(status_code=404,detail='Reservation not found!!')
    
    reservation.status = 'cancelled'

    db.commit()
    return JSONResponse(status_code=201,content={'message': 'Book Reserved Cancelled Successfully'})


@app.get('/reserve/my')
def my_reservation(user : user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild Authentication")

    reservation = db.query(Reservations).filter(Reservations.user_id == user.get('id')).all()
    return reservation


@app.get('/issues/my')
def my_issued_book(user : user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild Authentication")

    issues = db.query(IssueRecords).filter(
        IssueRecords.user_id == user.get('id'),
        IssueRecords.status == 'issued').all()
    return issues

