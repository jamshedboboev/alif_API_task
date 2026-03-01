import requests
from fastapi import FastAPI


app = FastAPI()

@app.get("/currency")
async def get_currency():
    r = requests.get("https://open.er-api.com/v6/latest/USD")
    return r.text