import os

from _share import ddb_client, sqs_kwargs, sqs_queue_name
from dotenv import load_dotenv

from inference_engine.producer.producer import Producer


def send_messages(num: int = 10):
    client = Producer(
        queue_name=sqs_queue_name(),
        ddb_client=ddb_client(),
        **sqs_kwargs(),
    )

    for i in range(num):
        _ = client.post_non_blocking({"message_n": i})
    # return resp


if __name__ == "__main__":
    if dotenvfile := os.environ.get("DOTENV_FILE"):
        load_dotenv(dotenvfile, override=True)

    send_messages(int(os.environ.get("N_MESSAGES_TO_SEND", 10)))
