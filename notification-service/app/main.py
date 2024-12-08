# main.py
import pika
from fastapi import FastAPI, BackgroundTasks
import mailtrap as mt
import json
import time
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

app = FastAPI()

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

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "notifications"

def send_email(address, message):
    mail = mt.Mail(
    sender=mt.Address(email="hello@demomailtrap.com", name="Mailtrap Test"),
    to=[mt.Address(email=address)],
    subject="Transaction!",
    text=message,
    category="Integration Test",
    )
    client = mt.MailtrapClient(token="36c22e845c851b170613a6d9c5b6212c")
    response = client.send(mail)

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

def consume_notifications(callback):
    """Consume messages from RabbitMQ"""
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=callback,
        auto_ack=True
    )
    print("Waiting for notifications...")
    channel.start_consuming()

def process_notification(ch, method, properties, body):
    try:
        # Decode the JSON object
        notification = json.loads(body.decode())
        to_email = notification.get("to_email")
        message = notification.get("message")
        
        # Placeholder for sending the email
        send_email(address=to_email, message=message)

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
    except Exception as e:
        print(f"Error processing notification: {e}")

@app.on_event("startup")
def startup_event():
    def run_consumer():
        consume_notifications(process_notification)

    import threading
    threading.Thread(target=run_consumer, daemon=True).start()