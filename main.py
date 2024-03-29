from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to the list of allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
DATABASE_URL = os.environ['DATABASE_URL']


def fetch_supplier(supplier_id: int) -> Dict[str, Any]:
    connection = None

    if isinstance(supplier_id, str):
        try:
            supplier_id = int(supplier_id)
        except TypeError:
            raise HTTPException(status_code=404, detail="Supplier not found")

    elif not isinstance(supplier_id, int):
        raise HTTPException(status_code=404, detail="Supplier not found")

    else:  # is int
        pass

    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))

        try:
            id_val = cursor.fetchone()[0]
        except (IndexError, TypeError):
            raise HTTPException(status_code=404, detail="Supplier not found")

        try:
            id_val = int(id_val)
        except (TypeError, ValueError):
            print(f'Tried to convert {id_val} to int, but it is a type {type(id_val)}')
            pass
        cursor.close()

        # Standard properties ("standards" for brevity)
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            '''
            SELECT
                name, referral, phone_number, other_contacts, email_address,
                postal_address, gmap_link, gmap_coordinates, website, ranking, notes, cat_id
            FROM suppliers WHERE supplier_id = %s
            ''',
            (id_val,)
        )

        standards = cursor.fetchone()
        cursor.close()

        # Category-specfic custom properties ("customs" for brevity)
        cursor = connection.cursor()
        cursor.execute('SELECT field_name, field_value FROM custom_properties WHERE supplier_id = %s', (id_val,))
        customs = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()

        return {"supplier_id": id_val, "standard_properties": standards, "custom_properties": customs}

    finally:
        if connection is not None:
            connection.close()


def fetch_suppliers():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

    except (ConnectionError, psycopg2.Error, psycopg2.DatabaseError):
        raise HTTPException(status_code=404, detail="No Database connection")

    else:
        cursor.execute("SELECT supplier_id FROM suppliers")
        ids = cursor.fetchall()

        data = []
        for id_ in ids:
            try:
                parsed_row = fetch_supplier(id_[0])
                data.append(parsed_row)
            except IndexError:
                data.append({"supplier_id": id_, "error": "IndexError occurred."})

        return data

    finally:
        if connection:
            connection.close()


def get_grid_data():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    except (ConnectionError, psycopg2.Error, psycopg2.DatabaseError):
        raise HTTPException(status_code=404, detail="No Database connection")

    else:
        cursor.execute(
            """
            SELECT
                s.supplier_id,
                s.name AS supplier_name,
                s.referral,
                s.phone_number,
                s.email_address,
                s.gmap_link,
                s.ranking,
                c.abbreviation AS category_name,
                c.hex_bg_color,
                c.hex_fg_color,
                c.icon
            FROM suppliers s
            INNER JOIN categories c
            ON s.cat_id = c.cat_id;
            """
        )

        return cursor.fetchall()

    finally:
        if connection:
            connection.close()


@app.get("/autocomplete_data")
async def get_autocomplete_data():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute("SELECT name, supplier_id FROM suppliers")
    data = []

    for i in cursor.fetchall():
        supplier_item = {'id': i[1], 'name': i[0]}
        data.append(supplier_item)

    cursor.close()
    connection.close()
    return data


@app.get("/autocomplete_test")
async def get_autocomplete_data():
    # TODO: Safe-delete in production
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM autocomplete_view")
    data = []

    for i in cursor.fetchall():
        supplier_item = {
            'id': i[0],
            'name': i[1],
            'category': i[3],
            'background_color': i[4],
            'foreground_color': i[5]
        }
        data.append(supplier_item)

    cursor.close()
    connection.close()
    return data


@app.get("/grid_data")
async def grid_data():
    data = get_grid_data()
    return data

@app.get("/supplier/{supplier_id}")
async def get_supplier_id(supplier_id: int):
    # Returns supplier info for the given id
    data = fetch_supplier(supplier_id)
    return data


@app.get("/suppliers")
async def get_suppliers():
    # Returns all suppliers with complete details
    data = fetch_suppliers()
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
