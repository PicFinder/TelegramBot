FROM python:3.11

ENV BOT_TOKEN=${PROD_BOT_TOKEN}
ENV BACKEND_API_URL=${BACKEND_API_URL}

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
