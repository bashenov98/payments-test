from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
from .dependencies import  get_current_account
import pika
import json
import time
import requests

RABBITMQ_HOST = "rabbitmq"

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
    channel.queue_declare(queue="notifications", durable=True)

    notification = {
        "to_email": to_email,
        "message": message
    }

    channel.basic_publish(
        exchange='',
        routing_key="notifications",
        body=json.dumps(notification),
        properties=pika.BasicProperties(
            delivery_mode=2  # Makes message persistent
        )
    )
    print(f"Notification sent to queue: {notification}")
    connection.close()

    

def send_transaction_to_queue(transaction):
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue="transaction", durable=True)

    channel.basic_publish(
        exchange='',
        routing_key="transaction",
        body=json.dumps(transaction, indent=5),
        properties=pika.BasicProperties(
            delivery_mode=2  # 
        )
    )
    print(f"Notification sent to queue: {transaction}")
    connection.close()

def create_transaction_message(from_account_id, to_account_id, amount):
    return f"New transaction initiated: From Account {from_account_id} to Account {to_account_id} with Amount {amount:.2f}"

@app.post("/transactions", response_model=schemas.TransactionResponse)
def create_transaction(request: schemas.TransactionRequest, db: Session = Depends(get_db), current_account: models.Account = Depends(get_current_account)):
    try:
        transaction = crud.transfer_funds(
            db, 
            from_account_id=request.from_account_id, 
            to_account_id=request.to_account_id, 
            amount=request.amount
        )
        if transaction is None or transaction.from_account_id != current_account.id:
            raise HTTPException(status_code=404, detail="Account not found")
        message_text = create_transaction_message(from_account_id=request.from_account_id, to_account_id=request.to_account_id, amount=request.amount)
        send_notification_to_queue(to_email="azamat.han2007@gmail.com", message=message_text)
        send_transaction_to_queue(transaction.to_dict())
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during the transaction: " + str(e))

# Get all transactions
@app.get("/transactions", response_model=list[schemas.TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db), current_account: models.Account = Depends(get_current_account)):
    try:
        transactions = db.query(models.Transaction).all()

        if transactions is None or transactions.from_account_id != current_account.id:
            raise HTTPException(status_code=404, detail="Account not found")
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while fetching transactions")

@app.get("/transactions/{account_id}")
def read_transactions_by_account(account_id: int, db: Session = Depends(get_db), current_account: models.Account = Depends(get_current_account)):
    try:    
        transactions = crud.get_transactions_by_account(db, account_id)

        if transactions is None or transactions.from_account_id != current_account.id:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while fetching transactions")
    
    
@app.get("/rates")
def get_currency_rates():

    url = "https://www.bcc.kz/personal/get_app_courses/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  
        return extract_sell_rates( json.dumps(response.json(), indent=4) )
    
    except requests.exceptions.Timeout:
        print("Ошибка: Превышено время ожидания")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
    except ValueError:
        print("Ошибка: Ответ не в формате JSON")

    if transaction is None or from_account_id.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Account not found")
        
    return None  

def extract_sell_rates(json_string):
    try:
        json_data = json.loads(json_string)
        
        sell_rates = {
            "usd": json_data.get("usd_sell"),
            "eur": json_data.get("eur_sell"),
            "rub": json_data.get("rub_sell"),
            "gbp": json_data.get("gbp_sell")
        }
        
        return sell_rates
    except json.JSONDecodeError:
        print("Ошибка: Невалидный JSON.")
        return None
    
    
@app.get("/saldodraft/{account_id}")
def read_transactions_by_account(account_id: int, db: Session = Depends(get_db)):
    try:    
        transactions = crud.get_account_balance_with_drafts(db, account_id)
        return transactions
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching transactions:  {e}")
    