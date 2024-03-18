from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from json import JSONDecoder

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html = ""
    with open('index.html') as file:
        html = file.read()

    return html

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/directory")
async def get_directory(path_: str):
    decoder = JSONDecoder()
    decoder.decode("suppliers.json")
