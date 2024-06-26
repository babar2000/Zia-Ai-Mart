from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select
from pydantic import BaseModel, Field, KafkaDsn
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json

app = FastAPI()

DATABASE_URL = "postgresql://ziakhan:my_password@PostgresOrderCont:5432/mydatabase"
engine = create_engine(DATABASE_URL, echo=True)

class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    product_id: int
    user_id: int
    quantity: int
    status: str

class OrderCreate(BaseModel):
    product_id: int
    user_id: int
    quantity: int

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/orders/", response_model=Order)
def create_order(order: OrderCreate):
    with Session(engine) as session:
        db_order = Order.from_orm(order)
        db_order.status = "pending"
        session.add(db_order)
        session.commit()
        session.refresh(db_order)
        
        # Send event to Kafka
        producer = KafkaDsn.KafkaProducer(bootstrap_servers='kafka:9092')
        producer.send('order_created', json.dumps(db_order.dict()).encode('utf-8'))
        producer.close()
        
        return db_order

@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int):
    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.id == order_id)).first()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
