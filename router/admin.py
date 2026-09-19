from fastapi import APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
from models import Users,Books,Reservations,IssueRecords
from database import Sessionlocal
from typing import Annotated,Optional
from fastapi.responses import JSONResponse
from datetime import timedelta,datetime

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

class IssueBook(BaseModel):
    book_id : int
    user_id : int

def get_db():
    db = Sessionlocal()
    try:
        yield db 
    finally:
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

FINE_PER_DAY = 20

def calculate_fine(due_date: datetime,return_date: datetime):
    overdue_date = (return_date.date() - due_date.date()).days
    if overdue_date > 0:
        return round(overdue_date * FINE_PER_DAY, 2)
    else:
        return 0.0




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
def update_book(user:user_dependency,db : db_dependency,updatebook : UpdateBooks,book_id : int):

    if user is None or user.get('role') != 'librarian':
        raise HTTPException(status_code=401, detail='Faild Authentication')

    book = db.query(Books).filter(Books.id == book_id).first()
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


@router.post('/admin/create_issue')
def create_issue(user:user_dependency,db : db_dependency,issue_request : IssueBook):

    if user is None or user.get('role') != 'librarian':
        raise HTTPException(status_code=401, detail='Faild Authentication')

    book = db.query(Books).filter(Books.id == issue_request.book_id).first()
    if book is None:
        raise HTTPException(status_code=404,detail="Book not found")
    
    member = db.query(Users).filter(Users.id == issue_request.user_id).first()
    if member is None:
        raise HTTPException(status_code=404,detail="Member not found")

    if book.available_copies <= 0:
        raise HTTPException(status_code=400,detail="No copies Available")


    loan_days = 14
    issue_date = datetime.now
    
    issue_model = IssueRecords(
        book_id = issue_request.book_id,
        user_id = issue_request.user_id,
        issue_date = issue_date,
        due_date = issue_date + timedelta(days=loan_days),
        status = 'isssued'
    )
    book.available_copies -= 1

    reservation = db.query(Reservations).filter(
        Reservations.book_id == issue_request.book_id,
        Reservations.user_id == issue_request.user_id,
        Reservations.status == 'pending'
    )
    if reservation is not None:
        reservation.status = 'approved'

    db.add(issue_model)
    db.commit()

    return JSONResponse(status_code=201,content={'message': 'Book issued Successfully'})


@router.put('/admin/return_book/{issue_id}')
def return_book(user:user_dependency,db : db_dependency,issue_id : int):

    if user is None or user.get('role') != 'librarian':
        raise HTTPException(status_code=401, detail='Faild Authentication')

    issue = db.query(IssueRecords).filter(IssueRecords.id == issue_id).first()
    if issue is None:
        raise HTTPException(status_code=404,detail="Issue record not found")

    return_date = datetime.now
    fine = calculate_fine(issue.due_date,return_date)

    issue.return_date = return_date
    issue.status = 'returned'
    issue.fine_amount = fine
    
    book = db.query(Books).filter(Books.id == issue.book_id).first()
    if book is  not None:
        book.available_copies += 1

    db.commit()

    return JSONResponse(status_code=201,content={'message': 'Book returned Successfully','fine_amount' : fine})

@router.put('/admin/fine/pay/{issue_id}')
def fine_paid(user : user_dependency,db:db_dependency,issue_id:int):
    if user is None or user.get('role') != 'librarian':
        raise HTTPException(status_code=401, detail='Faild Authentication')

    issue = db.query(IssueRecords).filter(IssueRecords.id == issue_id).first()
    if issue is None:
        raise HTTPException(status_code=404,detail="Issue record not found")

    issue.fine_paid = True

    db.commit()

    return JSONResponse(status_code=200,content={'message': 'Fine paid Successfully'})
