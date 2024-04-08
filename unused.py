"""
Unused.py
Unused methods, please do not use these endpoints in production.
"""
# @app.get("/import_backup")
# async def import_csv(filepath: str = 'backup.csv'):
#     # For internal use only (for now). Imports a CSV directory in the Heroku database.
#     # We only work with CSS and Gmaps URLs in this place, so we import the library and declare the function locally.
#     import csv
#     INDICES = {
#         'Servizio': 0,
#         'Società': 1,
#         'Riferimento': 2,
#         'Recapito': 3,
#         'Altri recapiti': 4,
#         'Email': 5,
#         'Indirizzo': 6,
#         'Paese': 7,
#         'Note': 8,
#     }
#
#     try:
#         connection = psycopg2.connect(DATABASE_URL)
#         cursor = connection.cursor()
#     except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError) as conn_e:
#         print('A connection error occurred: ', conn_e)
#         return False
#
#     try:
#         with open(filepath, 'r', newline='') as csvfile:
#             csv_reader = csv.reader(csvfile, delimiter=";")
#
#             for row in csv_reader:
#                 try:
#                     servizio_val = int(row[INDICES['Servizio']]) if str(row[INDICES['Servizio']]).isdigit() else 999
#                     societa_val = row[INDICES['Società']] or None
#                     riferimento_val = row[INDICES['Riferimento']] or None
#                     recapito_val = row[INDICES['Recapito']] or None
#                     altri_recapiti_val = row[INDICES['Altri recapiti']] or None
#                     email_val = row[INDICES['Email']] or None
#                     indirizzo_val = row[INDICES['Indirizzo']] or None
#                     paese_val = row[INDICES['Paese']] or None
#                     note_val = row[INDICES['Note']] or None
#
#                 except IndexError as idx_e:
#                     print('An IndexError made it impossible to process a row: ', row, idx_e)
#                     return {"Error": f"{row}, {idx_e}"}
#
#                 cursor.execute(
#                     f'''
#                     INSERT INTO suppliers(name, referral, phone_number, other_contacts, email_address, postal_address, gmap_link, notes, cat_id)
#                     VALUES ('{societa_val}', '{riferimento_val}', '{recapito_val}', '{altri_recapiti_val}', '{email_val}', '{indirizzo_val}', '{get_gmaps_url(f'{societa_val} {indirizzo_val} {paese_val}')}', '{note_val}', {servizio_val});
#                     '''
#                 )
#
#             connection.commit()
#             cursor.close()
#             connection.close()
#             return True
#
#     except FileNotFoundError:
#         print("File not found.")
#         return False
#
#     except Exception as e:
#         print("An error occurred:", e)
#         return False