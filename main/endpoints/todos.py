from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from schema.todos_schema import Todo, TodoCreate, TodoRead
from core.db import get_db
from core.auth import verify_token

router = APIRouter()

@router.post("/", response_model=TodoRead, dependencies=[Depends(verify_token)])
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo.from_orm(todo)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.get("/", response_model=List[TodoRead], dependencies=[Depends(verify_token)])
async def list_todos(db: Session = Depends(get_db)):
    todos = db.exec(select(Todo)).all()
    return todos

@router.get("/{todo_id}", response_model=TodoRead, dependencies=[Depends(verify_token)])
async def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
