from fastapi import FastAPI, Depends, HTTPException
from schemas import Todo as Todoschema, TodoCreate
from sqlalchemy.orm import Session
from database import Base, sessionlocal, engine
from models import Todo

Base.metadata.create_all(bind = engine)
app = FastAPI()

#Dependeny for db session
def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

#POST - Create TODO
@app.post("/todos", response_model = Todoschema)
def create(todo : TodoCreate, db : Session = Depends(get_db)):
    db_todo = Todo(**todo.dict()) #model
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos", response_model = list[Todoschema])
def read_todos(db : Session = Depends(get_db)):
    return db.query(Todo).all()

@app.get("/todos/{id}", response_model = Todoschema)
def read_todo (id : int, db : Session = Depends(get_db)):
    result = db.query(Todo).filter(Todo.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail = f'id {id} not found')
    else:
        return result

@app.put("/todos/{id}", response_model = Todoschema)
def update_todo(id : int, updated : TodoCreate, db : Session = Depends(get_db)):
    result = db.query(Todo).filter(Todo.id ==id).first()
    if not result:
        raise HTTPException(status_code = 404, detail = f'Invalid Id : {id}')
    else:
        result.title = updated.title
        result.description = updated.description
        result.completed = updated.completed
        db.commit()
        db.refresh(result)
        return result

@app.delete("/todos/{id}")
def delete_todo(id:int, db : Session = Depends(get_db)):
    result = db.query(Todo).filter(Todo.id == id).first()
    if not result:
        raise HTTPException(status_code = 404, detail = f'{id} is not valid')
    else:
        db.delete(result)
        db.commit()
        return {"Message": "Deleted successfully"}

