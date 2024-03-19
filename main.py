from fastapi import FastAPI
import psycopg2
import os


DATABASE_URL = os.environ['DATABASE_URL']
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def hworld(name: str):
    return {"message": f"hello, {name}"}


@app.get("/autocomplete_data")
async def get_autocomplete_data():
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM test WHERE test_id = 1")

        return cursor.fetchall()

    except psycopg2.Error as e:
        return {"message": f"error occurred: {e}"}