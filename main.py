from fastapi import FastAPI
import psycopg2
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
    connection = psycopg2.connection(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute("""SELECT * FROM test WHERE test_id = 1""")
    data = cursor.fetchall()

    return data
