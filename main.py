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
        # connection = psycopg2.connect(
        #     database="dfg7578eodbk83",
        #     host="cdgn4ufq38ipd0.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com",
        #     user="ub72dcmj38e4l2",
        #     password="p3d3b7bc9f84595d79b5e170cef0107c5cc78eda29be0dfc4c4127fb1c80077b7",
        #     port="5432"
        # )

        cursor = connection.cursor()

        return cursor.fetchall(
            "SELECT * FROM test WHERE test_id = 1"
        )

    except (ConnectionError, ConnectionRefusedError) as e:
        return {"message": f"error occurred: {e}"}

