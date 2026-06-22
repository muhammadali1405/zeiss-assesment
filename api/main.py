from fastapi import FastAPI
from pydantic import BaseModel
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential
import threading
import os
import json
import time
from contextlib import asynccontextmanager

# Environment Variables
SERVICE_BUS_FQDN = os.getenv(
    "SERVICE_BUS_FQDN"
)

QUEUE_NAME = os.getenv(
    "SERVICE_BUS_QUEUE_NAME",
    "work-queue"
)

if not SERVICE_BUS_FQDN:
    raise ValueError(
        "SERVICE_BUS_FQDN environment variable is not set. Please add in KeyVault and Env"
    )

credential = DefaultAzureCredential()

processed_items = []


# Background Worker
def servicebus_worker():
    while True:
        try:
            print("Background worker started...")
            with ServiceBusClient(
                fully_qualified_namespace=SERVICE_BUS_FQDN,
                credential=credential
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
                                body = str(msg)
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
                                print(
                                    f"Error processing message: {ex}"
                                )
                                receiver.abandon_message(msg)

        except Exception as ex:
            print(
                f"Worker connection error: {ex}"
            )
            time.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):

    threading.Thread(
        target=servicebus_worker,
        daemon=True
    ).start()

    yield


app = FastAPI(
    lifespan=lifespan
)


class WorkItem(BaseModel):
    id: int
    message: str


# POST /api/work
@app.post("/api/work")
def enqueue_work(work: WorkItem):

    with ServiceBusClient(
        fully_qualified_namespace=SERVICE_BUS_FQDN,
        credential=credential
    ) as client:

        sender = client.get_queue_sender(
            queue_name=QUEUE_NAME
        )

        with sender:

            sender.send_messages(
                ServiceBusMessage(
                    json.dumps(
                        work.model_dump()
                    )
                )
            )

    return {
        "message": "Work item queued successfully",
        "work": work
    }


# GET /health/live
@app.get("/health/live")
def liveness():

    return {
        "status": "Live"
    }


# GET /health/ready
@app.get("/health/ready")
def readiness():

    try:

        with ServiceBusClient(
            fully_qualified_namespace=SERVICE_BUS_FQDN,
            credential=credential
        ):
            return {
                "status": "Ready"
            }

    except Exception:

        return {
            "status": "Not Ready"
        }


# GET /api/work
@app.get("/api/work")
def get_processed_work():

    return {
        "count": len(processed_items),
        "items": processed_items
    }
