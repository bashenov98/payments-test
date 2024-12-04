from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
import pika
import json
import time

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "notifications"

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_connection():
    """Establish connection to RabbitMQ"""
    credentials = pika.PlainCredentials('user', 'password')
    parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
    for attempt in range(5):
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection attempt {attempt + 1} failed. Retrying in 5 seconds...")
            time.sleep(5)
    raise Exception("Unable to connect to RabbitMQ after 5 attempts")


def send_notification_to_queue(to_email, message):
    """Publish JSON object to RabbitMQ"""
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    notification = {
        "to_email": to_email,
        "message": message
    }

    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=json.dumps(notification),
        properties=pika.BasicProperties(
            delivery_mode=2  # Makes message persistent
        )
    )
    print(f"Notification sent to queue: {notification}")
    connection.close()

def create_transaction_message(from_account_id, to_account_id, amount):
    return f"New transaction initiated: From Account {from_account_id} to Account {to_account_id} with Amount {amount:.2f}"

@app.post("/transactions", response_model=schemas.TransactionResponse)
def create_transaction(request: schemas.TransactionRequest, db: Session = Depends(get_db)):
    try:
        transaction = crud.transfer_funds(
            db, 
            from_account_id=request.from_account_id, 
            to_account_id=request.to_account_id, 
            amount=request.amount
        )
        message_text = create_transaction_message(from_account_id=request.from_account_id, to_account_id=request.to_account_id, amount=request.amount)
        send_notification_to_queue(to_email="bashenov98@gmail.com", message=message_text)

        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during the transaction")

# Get all transactions
@app.get("/transactions", response_model=list[schemas.TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db)):
    try:
        transactions = db.query(models.Transaction).all()
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while fetching transactions")

@app.get("/transactions/{account_id}")
def read_transactions_by_account(account_id: int, db: Session = Depends(get_db)):
    try:    
        transactions = crud.get_transactions_by_account(db, account_id)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while fetching transactions")