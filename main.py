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
async def import_csv(filepath: str = 'backup.csv'):
    # For internal use only (for now). Imports a CSV directory in the Heroku database.
    # Servizio; Società; Riferimento; Recapito; Altri recapiti; Email; Indirizzo; Paese; Note
    import csv  # We only work with CSS in this place.

    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
    except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError) as conn_e:
        print('A connection error occurred: ', conn_e)
        return False

    try:
        with open(filepath, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            str_ = str()  # debug

            for row in csv_reader:
                str_ += f"{row}\n"

            return str_

    except FileNotFoundError:
        print("File not found.")
        return False
    except Exception as e:
        print("An error occurred:", e)
        return False

    '''
    cursor.execute("SELECT name FROM categories")
    data = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()
    '''

if __name__ == '__main__':
    import_csv('')

