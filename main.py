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
    data = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()
    return data


@app.get("/import_backup")
async def import_csv(filepath: str = 'backup.csv') -> bool:
    # For internal use only (for now). Imports a CSV directory in the Heroku database.
    # Servizio; Società; Riferimento; Recapito; Altri recapiti; Email; Indirizzo; Paese; Note
    return False

if __name__ == '__main__':
    import_csv('')

