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

    def generate_google_maps_url(search_query):
        base_url = "https://www.google.com/maps/search/?api=1&query="
        encoded_query = '+'.join(search_query.split())  # Encode search query
        return base_url + encoded_query

    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
    except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError) as conn_e:
        print('A connection error occurred: ', conn_e)
        return False

    try:
        with open(filepath, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)

            for row in csv_reader:
                try:
                    servizio_val = row[INDICES['Servizio']] or None
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
                    VALUES ({societa_val}, {riferimento_val}, {recapito_val}, {altri_recapiti_val}, {email_val}, {indirizzo_val}, {generate_google_maps_url(f'{societa_val} {indirizzo_val} {paese_val}')}, {note_val}, {servizio_val});
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

if __name__ == '__main__':
    import_csv('')

