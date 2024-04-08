from typing import Dict, Any
from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import os
import tempfile
import paramiko

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to the list of allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ['DATABASE_URL']
SFTP_HOST = os.getenv('SFTP_HOST')
SFTP_PORT = 22
SFTP_USERNAME = os.getenv('SFTP_USERNAME')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')


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
                s.other_contacts,
                s.gmap_link,
                s.ranking,
                c.abbreviation AS category_abbr,
                c.name as category_name,
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


@app.get("/")
async def root():
    return {"message": "Hello World"}


def sftp_upload_file(file_path, filename):
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    sftp = None
    try:
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Check if the file exists before upload
        if not os.path.exists(file_path):
            print(f"File does not exist: {file_path}")
            return

        sftp.put(file_path, f'profilepics/{filename}')
    except Exception as e:
        print(f"Failed to upload file due to: {e}. Filepath: {file_path}. Filename: {filename}.")
    finally:
        if sftp:
            sftp.close()
        transport.close()
        if os.path.exists(file_path):
            os.remove(file_path)  # Clean up the temp file after an upload attempt


@app.post("/uploadpic/")
async def create_upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Use a dedicated temporary file to avoid name conflicts and ensure it's in a writable directory
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    content = await file.read()
    temp_file.write(content)
    temp_file.close()  # Important to close the file to flush writes and avoid locking issues

    # Now the file is saved, and we have an absolute path to it
    # Schedule the SFTP upload as a background task
    background_tasks.add_task(sftp_upload_file, temp_file_path, file.filename)

    return {"filename": file.filename, "detail": "File upload initiated. The file will be uploaded in the background."}