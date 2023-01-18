FROM python:3.10.5-bullseye

RUN adduser collector

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt 

COPY store-data.py .

USER collector

CMD ["python", "store-data.py"]
