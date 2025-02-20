"""
This is the main module for the Rent-Ease API application.
It uses FastAPI to create a simple API with a root endpoint and a health check endpoint.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

import requests

app = FastAPI(root_path="/api", title="Rent-Ease API")

@app.get("/")
def read_root():
    return {"message": "Hello, Rent-Ease!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/cat-fact")
def get_cat_fact():
    response = requests.get("https://catfact.ninja/fact")
    if response.status_code == 200:
        return response.json()
    else:
        return JSONResponse(status_code=404, content={"message": "No positions found"})
