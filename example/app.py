import os
import time

from _share import create_queue, create_table
from _share import ddb_client as get_ddb_client
from _share import sqs_kwargs, sqs_queue_name
from dotenv import load_dotenv
from logzero import logger

from inference_engine.consumer.api_wrapper import get_app
from inference_engine.consumer.consumer import Consumer

if dotenvfile := os.environ.get("DOTENV_FILE"):
    load_dotenv(dotenvfile, override=True)


if os.environ.get("DDB_CREATE_TABLE", "false").lower() == "true":
    create_table(tolerate_already_exists=True)

if os.environ.get("SQS_CREATE_QUEUE", "false").lower() == "true":
    create_queue()


ddb_client = get_ddb_client()


def compute_function(body, message_id) -> dict:
    logger.info("Got message, body=%s, message_id: %s", body, message_id)
    sleep4 = (
        body.get("FUNCTION_PROC_TIME")
        or os.environ.get("FUNCTION_PROC_TIME")
        or 0.1
    )
    sleep4 = float(sleep4)
    time.sleep(sleep4)

    return {"recieved_message_body": body, "message_id": message_id}


consumer = Consumer(
    queue_name=sqs_queue_name(),
    ddb_client=ddb_client,
    compute_result=compute_function,
    enable_ecs_scalein_protection=(
        os.environ.get("ENABLE_ECS_SCALEIN_PROTECTION", "true").lower()
        == "true"
    ),
    heartbeat_visibility_timeout=int(
        os.environ.get("HEARTBEAT_VISIBILITY_TIMEOUT", 30)
    ),
    heartbeat_interval=float(os.environ.get("HEARTBEAT_INTERVAL", 10)),
    **sqs_kwargs(),
)
consumer.start_consuming()
app = get_app(consumer)
time.sleep(1)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")
