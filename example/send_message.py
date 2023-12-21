import os

from _share import ddb_client, sqs_kwargs, sqs_queue_name
from dotenv import load_dotenv

from inference_engine.producer.producer import Producer, Response


def send_message() -> Response:
    client = Producer(
        queue_name=sqs_queue_name(),
        ddb_client=ddb_client(),
        **sqs_kwargs(),
    )

    resp = client.post({"parameters": [1, 2, 3]})
    return resp


if __name__ == "__main__":
    if dotenvfile := os.environ.get("DOTENV_FILE"):
        load_dotenv(dotenvfile, override=True)

    print(send_message())
