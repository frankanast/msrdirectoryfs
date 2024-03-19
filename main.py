from json import JSONDecoder
import psycopg2
from fastapi import FastAPI, Request

app = FastAPI()
# connection = psycopg2.connect(
#     database="db_name",
#     host="db_host",
#     user="db_user",
#     password="db_pass",
#     port="db_port"
# )
# cursor = connection.cursor()


@app.get("/")
async def read_root(request: Request):
    return {"hello": "world"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/directory")
async def get_directory(path_: str):
    decoder = JSONDecoder()
    decoder.decode("suppliers.json")
