from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select
from pydantic import BaseModel, Field

app = FastAPI()

DATABASE_URL = "postgresql://ziakhan:my_password@PostgresPaymentCont:5432/mydatabase"
engine = create_engine(DATABASE_URL, echo=True)

class Payment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    order_id: int
    amount: float
    status: str

class PaymentCreate(BaseModel):
    order_id: int
    amount: float

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/payments/", response_model=Payment)
def create_payment(payment: PaymentCreate):
    with Session(engine) as session:
        db_payment = Payment.from_orm(payment)
        db_payment.status = "pending"
        session.add(db_payment)
        session.commit()
        session.refresh(db_payment)
        return db_payment

@app.get("/payments/{payment_id}", response_model=Payment)
def read_payment(payment_id: int):
    with Session(engine) as session:
        payment = session.exec(select(Payment).where(Payment.id == payment_id)).first()
        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
