from fastapi import FastAPI
from app.api import endpoints

app = FastAPI(title="Travelling Salesman Problem API")
app.include_router(endpoints.router)