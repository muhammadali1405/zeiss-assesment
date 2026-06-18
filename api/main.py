from fastapi import FastAPI
from pydantic import BaseModel
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from queue import Queue
import threading
import os
import json
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):

    threading.Thread(
        target=servicebus_worker,
        daemon=True
    ).start()

    yield


app = FastAPI(lifespan=lifespan)
work_queue = Queue()

processed_items = []

# Namespace : sb-zeiss-ns-01
# Queue     : work-queue
SERVICE_BUS_CONNECTION_STRING = os.getenv(
    "SERVICE_BUS_CONNECTION_STRING"
)

QUEUE_NAME = os.getenv(
    "SERVICE_BUS_QUEUE_NAME",
    "work-queue"
)

class WorkItem(BaseModel):
    id: int
    message: str

# Background Worker
def servicebus_worker():
    print("Background worker started...")
    with ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STRING
    ) as client:
        receiver = client.get_queue_receiver(
            queue_name=QUEUE_NAME
        )
        with receiver:
            while True:
                messages = receiver.receive_messages(
                    max_message_count=10,
                    max_wait_time=5
                )
                for msg in messages:
                    try:
                        body = b"".join(
                            [bytes(part) for part in msg.body]
                        ).decode("utf-8")
                        work_item = json.loads(body)
                        print(
                            f"Processing message: {work_item}"
                        )
                        processed_items.append({
                            "id": work_item["id"],
                            "message": work_item["message"],
                            "status": "Processed"
                        })
                        receiver.complete_message(msg)
                    except Exception as ex:
                        print(f"Error processing message: {ex}")

@app.on_event("startup")
def startup_event():

    threading.Thread(
        target=servicebus_worker,
        daemon=True
    ).start()

# POST /api/work
@app.post("/api/work")
def enqueue_work(work: WorkItem):

    with ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STRING
    ) as client:

        sender = client.get_queue_sender(
            queue_name=QUEUE_NAME
        )

        with sender:

            sender.send_messages(
                ServiceBusMessage(
                    json.dumps(work.model_dump())
                )
            )

    return {
        "message": "Work item queued successfully",
        "work": work
    }

# GET /health/live
@app.get("/health/live")
def liveness():
    return {"status": "Live"}

# GET /health/ready
@app.get("/health/ready")
def readiness():
    return {"status": "Ready"}



@app.post("/api/work")
def enqueue_work(work: WorkItem):
    with ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STRING
    ) as client:
        sender = client.get_queue_sender(
            queue_name=QUEUE_NAME
        )
        with sender:
            sender.send_messages(
                ServiceBusMessage(
                    json.dumps(work.model_dump())
                )
            )
    return {
        "message": "Work item queued successfully",
        "work": work
    }
# GET /api/work
@app.get("/api/work")
def get_processed_work():

    return {
        "count": len(processed_items),
        "items": processed_items
    }