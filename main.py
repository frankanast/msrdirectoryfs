from fastapi import FastAPI
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
    return DATABASE_URL
