FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl

WORKDIR /etc/app/

COPY src src
COPY pyproject.toml .
COPY example/requirements.txt requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY example/app.py .
COPY example/_share.py .
COPY example/run.sh run.sh

CMD ["./run.sh"]
