FROM python:3.13-bullseye

ENV PYTHONBUFFERED=1

WORKDIR /tg_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
