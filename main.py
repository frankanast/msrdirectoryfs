from typing import Dict, Any
from fastapi import FastAPI, HTTPException
import psycopg2
from json import JSONDecoder, JSONEncoder
import os

app = FastAPI()
DATABASE_URL = os.environ['DATABASE_URL']


def fetch_supplier(supplier_id: int) -> Dict[str, Any]:
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Supplier not found")

        columns = [desc[0] for desc in cursor.description]
        properties = {columns[i]: result[i] for i in range(len(columns))}

        return {"supplier_id": supplier_id, "properties": properties}
    finally:
        cursor.close()
        if connection is not None:
            connection.close()


@app.get("/autocomplete_data")
async def get_autocomplete_data():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute("SELECT name, supplier_id FROM suppliers")
    data = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.close()
    connection.close()
    return data


@app.get("/parse_properties/{supplier_id}")
async def get_supplier_id(supplier_id: int):
    # Returns supplier info for the given id
    data = fetch_supplier(supplier_id)
    return data


@app.get("get_gmaps_url/{search_query}")
async def get_gmaps_url(search_query):
    base_url = "https://www.google.com/maps/search/?api=1&query="
    encoded_query = '+'.join(search_query.split())  # Encode search query
    return base_url + encoded_query


# Debug/Helper functions
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def hworld(name: str):
    return {"message": f"hello, {name}"}


@app.get("/import_backup")
async def import_csv(filepath: str = 'backup.csv'):
    # For internal use only (for now). Imports a CSV directory in the Heroku database.
    # We only work with CSS and Gmaps URLs in this place, so we import the library and declare the function locally.
    import csv
    INDICES = {
        'Servizio': 0,
        'Società': 1,
        'Riferimento': 2,
        'Recapito': 3,
        'Altri recapiti': 4,
        'Email': 5,
        'Indirizzo': 6,
        'Paese': 7,
        'Note': 8,
    }

    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
    except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError) as conn_e:
        print('A connection error occurred: ', conn_e)
        return False

    try:
        with open(filepath, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";")

            for row in csv_reader:
                try:
                    servizio_val = int(row[INDICES['Servizio']]) if str(row[INDICES['Servizio']]).isdigit() else 999
                    societa_val = row[INDICES['Società']] or None
                    riferimento_val = row[INDICES['Riferimento']] or None
                    recapito_val = row[INDICES['Recapito']] or None
                    altri_recapiti_val = row[INDICES['Altri recapiti']] or None
                    email_val = row[INDICES['Email']] or None
                    indirizzo_val = row[INDICES['Indirizzo']] or None
                    paese_val = row[INDICES['Paese']] or None
                    note_val = row[INDICES['Note']] or None

                except IndexError as idx_e:
                    print('An IndexError made it impossible to process a row: ', row, idx_e)
                    return {"Error": f"{row}, {idx_e}"}

                cursor.execute(
                    f'''
                    INSERT INTO suppliers(name, referral, phone_number, other_contacts, email_address, postal_address, gmap_link, notes, cat_id)  
                    VALUES ('{societa_val}', '{riferimento_val}', '{recapito_val}', '{altri_recapiti_val}', '{email_val}', '{indirizzo_val}', '{get_gmaps_url(f'{societa_val} {indirizzo_val} {paese_val}')}', '{note_val}', {servizio_val});
                    '''
                )

            connection.commit()
            cursor.close()
            connection.close()
            return True

    except FileNotFoundError:
        print("File not found.")
        return False

    except Exception as e:
        print("An error occurred:", e)
        return False
