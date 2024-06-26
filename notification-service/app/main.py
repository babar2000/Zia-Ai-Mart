import threading
from fastapi import FastAPI, HTTPException
from kafka import KafkaConsumer
import json

app = FastAPI()

consumer = KafkaConsumer(
    'order_created',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    group_id='notification_service'
)

@app.post("/notifications/")
def send_notification(message: str):
    # Here, you would implement the actual notification sending logic (e.g., email, SMS)
    print(f"Notification sent: {message}")
    return {"message": "Notification sent"}

@app.on_event("startup")
def startup_event():
    def consume():
        for message in consumer:
            order = json.loads(message.value.decode('utf-8'))
            send_notification(f"Order created: {order}")
    threading.Thread(target=consume).start()
