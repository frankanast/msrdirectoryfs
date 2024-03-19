import json

from fastapi import FastAPI
import psycopg2
from json import JSONDecoder, JSONEncoder
import os

app = FastAPI()
DATABASE_URL = os.environ['DATABASE_URL']

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def hworld(name: str):
    return {"message": f"hello, {name}"}


@app.get("/autocomplete_data")
async def get_autocomplete_data():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM categories")
    rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append(dict(row))
    data = json.dumps(results)

    cursor.close()
    connection.close()
    return data

