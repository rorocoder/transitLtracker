from fastapi import FastAPI
from src.main import get_trips

app = FastAPI()

@app.get("/trips")
def trips():
    return get_trips()