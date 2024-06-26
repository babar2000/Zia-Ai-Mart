from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select
from pydantic import BaseModel, Field

app = FastAPI()

DATABASE_URL = "postgresql://ziakhan:my_password@PostgresUserCont:5432/mydatabase"
engine = create_engine(DATABASE_URL, echo=True)

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str

class UserCreate(BaseModel):
    name: str
    email: str

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
    with Session(engine) as session:
        db_user = User.from_orm(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
