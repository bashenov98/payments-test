from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
from .dependencies import  get_current_account
import pika
import json
import time
import requests
import threading
from redis import Redis
# from starlette_exporter import handle_metrics, PrometheusMiddleware
from .middleware import LoggingMiddleware
from .logger import get_logger
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

RABBITMQ_HOST = "rabbitmq"

redis_client = Redis(host="redis", port=6379, decode_responses=True)
CURRENCY_RATES_KEY = "currency_rates"
FETCH_INTERVAL = 3600

# Create tables
models.Base.metadata.create_all(bind=engine)

log = get_logger("transaction-service")

app = FastAPI()

app.add_middleware(LoggingMiddleware)
log.info("Application initialized")

REQUEST_COUNT = Counter('request_count', 'Number of requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])

@app.middleware("http")
async def add_prometheus_middleware(request, call_next):
    endpoint = request.url.path
    method = request.method
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    with REQUEST_LATENCY.labels(endpoint=endpoint).time():
        response = await call_next(request)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

def get_connection():
    """Establish connection to RabbitMQ"""
    credentials = pika.PlainCredentials('user', 'password')
    parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
    for attempt in range(5):
        try:
            log.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1})")
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            log.warning(f"RabbitMQ connection attempt {attempt + 1} failed. Retrying...")
            time.sleep(5)
    log.error("Unable to connect to RabbitMQ after 5 attempts")
    raise Exception("Unable to connect to RabbitMQ after 5 attempts")


def send_notification_to_queue(to_email, message):
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.queue_declare(queue="notifications", durable=True)

        notification = {"to_email": to_email, "message": message}

        channel.basic_publish(
            exchange='',
            routing_key="notifications",
            body=json.dumps(notification),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        log.info(f"Notification sent to queue: {notification}")
        connection.close()
    except Exception as e:
        log.error(f"Error sending notification to RabbitMQ: {e}")

    

def send_transaction_to_queue(transaction):
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.queue_declare(queue="transaction", durable=True)

        channel.basic_publish(
            exchange='',
            routing_key="transaction",
            body=json.dumps(transaction, indent=5),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        log.info(f"Transaction sent to queue: {transaction}")
        connection.close()
    except Exception as e:
        log.error(f"Error sending transaction to RabbitMQ: {e}")

def create_transaction_message(from_account_id, to_account_id, amount):
    return f"New transaction initiated: From Account {from_account_id} to Account {to_account_id} with Amount {amount:.2f}"

@app.post("/transactions", response_model=schemas.TransactionResponse)
def create_transaction(request: schemas.TransactionRequest, db: Session = Depends(get_db)):
    try:
        log.info(f"Creating transaction: {request}")
        transaction = crud.create_pending_transaction(
            db, 
            from_account_id=request.from_account_id, 
            to_account_id=request.to_account_id, 
            amount=request.amount,
            currency=request.currency,
            rate=json.dumps(get_currency_rates())
        )
        message_text = create_transaction_message(from_account_id=request.from_account_id, to_account_id=request.to_account_id, amount=request.amount)
        send_notification_to_queue(to_email="azamat.han2007@gmail.com", message=message_text)
        send_transaction_to_queue(transaction.to_dict())
        log.info(f"Transaction created successfully: {transaction}")
        return transaction
    except ValueError as e:
        log.error(f"Transaction failed with ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error during transaction creation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the transaction: " + str(e))

@app.post("/replenishment", response_model=schemas.ReplenishmentResponse)
def create_replenishment(request: schemas.ReplenishmentRequest, db: Session = Depends(get_db)):
    try:
        log.info(f"Creating replenishment: {request}")
        replenishment = crud.create_pending_replenishment(
            db, 
            from_=request.from_, 
            to_account_id=request.to_account_id, 
            amount=request.amount,
            currency=request.currency,
            rate=json.dumps(get_currency_rates())
        )
        #message_text = create_transaction_message(from_account_id=request.from_account_id, to_account_id=request.to_account_id, amount=request.amount)
        #send_notification_to_queue(to_email="azamat.han2007@gmail.com", message="message_text")
        send_transaction_to_queue(replenishment.to_dict())
        log.info(f"replenishment created successfully: {replenishment}")
        return replenishment
    except ValueError as e:
        log.error(f"replenishment failed with ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error during replenishment creation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the replenishment: " + str(e))

@app.post("/withdrawal", response_model=schemas.WithdrawalResponse)
def create_withdrawal(request: schemas.WithdrawalRequest, db: Session = Depends(get_db)):
    try:
        log.info(f"Creating withdrawal: {request}")
        withdrawal = crud.create_pending_withdrawal(
            db, 
            from_account_id=request.from_account_id, 
            to_=request.to_, 
            amount=request.amount,
            currency=request.currency,
            rate=json.dumps(get_currency_rates())
        )
        #message_text = create_transaction_message(from_account_id=request.from_account_id, to_account_id=request.to_account_id, amount=request.amount)
        #send_notification_to_queue(to_email="azamat.han2007@gmail.com", message="message_text")
        send_transaction_to_queue(withdrawal.to_dict())
        log.info(f"withdrawal created successfully: {withdrawal}")
        return withdrawal
    except ValueError as e:
        log.error(f"withdrawal failed with ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Unexpected error during withdrawal creation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the withdrawal: " + str(e))

# Get all transactions
@app.get("/transactions", response_model=list[schemas.TransactionResponse])
def get_all_transactions(db: Session = Depends(get_db)):
    try:
        log.info("Fetching all transactions")
        transactions = db.query(models.Transaction).all()
        return transactions
    except Exception as e:
        log.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching transactions")

@app.get("/transactions/{account_id}")
def read_transactions_by_account(account_id: int, db: Session = Depends(get_db)):
    try:    
        log.info(f"Fetching transactions for account: {account_id}")
        transactions = crud.get_transactions_by_account(db, account_id)
        return transactions
    except Exception as e:
        log.error(f"Error fetching transactions for account {account_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching transactions")
    

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

@app.on_event("startup")
async def startup_event():
    log.info("Starting up application")
    thread = threading.Thread(target=schedule_rates_fetch, daemon=True)
    thread.start()

def fetch_currency_rates():
    url = "https://www.bcc.kz/personal/get_app_courses/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  
        rates = extract_sell_rates( json.dumps(response.json(), indent=4) )
        redis_client.set(CURRENCY_RATES_KEY, json.dumps(rates))
        log.info(f"Currency rates updated: {rates}")
    except requests.exceptions.Timeout:
        log.warning("Currency rate fetch timeout")
    except requests.exceptions.RequestException as e:
        log.error(f"Currency rate fetch error: {e}")
    except ValueError:
        log.error("Currency rate response not in JSON format")

def schedule_rates_fetch():
    """
    Periodically fetch currency rates every hour.
    """
    while True:
        fetch_currency_rates()
        time.sleep(FETCH_INTERVAL)

@app.get("/rates")
def get_currency_rates():
    """
    Fetches the latest currency rates from Redis and returns them.
    """
    rates = redis_client.get(CURRENCY_RATES_KEY)
    if rates:
        log.info("Returning cached currency rates")
        return json.loads(rates)
    log.warning("Currency rates not available")
    return {"error": "Currency rates not available."}

@app.get("/saldodraft/{account_id}")
def read_transactions_by_account(account_id: int, db: Session = Depends(get_db)):
    try:    
        transactions = crud.get_account_balance_with_drafts(db, account_id)
        return transactions
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching transactions:  {e}")
    