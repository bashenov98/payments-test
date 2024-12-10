# app/main.py
import pika
from fastapi import FastAPI
from fastapi import Depends
from .routers import accounts
from sqlalchemy.orm import Session
import time
import json
from .database import engine, SessionLocal
from . import models
from . import crud
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
from .routers.accounts import Operation
from .dependencies import get_db

models.Base.metadata.create_all(bind=engine)

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "transaction"

app = FastAPI(
    title="Account Service API",
    description="API для управления счетами пользователей",
    version="1.0.0",
)

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

app.include_router(accounts.router)

def consume_transaction(callback):
    """Consume messages from RabbitMQ"""
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=callback,
        auto_ack=True
    )
    print("Waiting for transaction...")
    channel.start_consuming()

def get_connection():
    """Establish connection to RabbitMQ"""
    credentials = pika.PlainCredentials('user', 'password')
    parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
    for attempt in range(10):
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection attempt {attempt + 1} failed. Retrying in 5 seconds...")
            time.sleep(5)
    raise Exception("Unable to connect to RabbitMQ after 5 attempts")

def process_transaction_rabbit(body, db: Session):
    try:
        # Decode the JSON object
        transaction = json.loads(body.decode())
        # Get the name field
        name = transaction.get("name")
        if name == "transactions":
            crud.process_transaction(db=db,body=body)
        elif name == "replenishment":
            crud.process_replenishment(db=db,body=body)
        elif name == "withdrawal":
            crud.process_withdrawal(db=db,body=body)
        else:
            print("Unknown name:", name)
        UPD = {
            "name" :name,
            "id" :transaction.get("id"),
            "status": "completed",
            "message": "done"
        }
        send_transaction_to_queue(UPD)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        UPD = {
            "name" :json.loads(body.decode()).get("name"),
            "id" :json.loads(body.decode()).get("id"),
            "status": "error",
            "message": str(e)
        }
        send_transaction_to_queue(UPD)
    except Exception as e:
        print(f"Error processing transaction: {e}")
        UPD = {
            "name" :json.loads(body.decode()).get("name"),
            "id" :json.loads(body.decode()).get("id"),
            "status": "error",
            "message": str(e)
        }
        send_transaction_to_queue(UPD)
        print(f"Sending transaction: {UPD}")

@app.on_event("startup")
def startup_event():
    def run_consumer():
        # Inject DB session into consumer
        with SessionLocal() as db:
            consume_transaction(lambda ch, method, properties, body: process_transaction_rabbit(body, db))

    import threading
    threading.Thread(target=run_consumer, daemon=True).start()

        
def send_transaction_to_queue(transaction):
    try:
        print(f"Sending send_transaction_to_queue transaction: {transaction}")
        connection = get_connection()
        channel = connection.channel()
        channel.queue_declare(queue="transactonUPD", durable=True)

        channel.basic_publish(
            exchange='',
            routing_key="transactonUPD",
            body=json.dumps(transaction, indent=3),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        # log.info(f"Transaction sent to queue: {transaction}")
        connection.close()
    except Exception as e:
        print(f"Error processing transaction: {e}")
        # log.error(f"Error sending transaction to RabbitMQ: {e}")