FROM python:3.10

EXPOSE ${PORT}

WORKDIR /code

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "${HOST}", "--port", "${PORT}", "--reload=${RELOAD}"]

