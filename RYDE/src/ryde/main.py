from fastapi import FastAPI
from src.ryde.controllers import HealthCheckController, GeneralStatisticsController

app = FastAPI(title = "RYDE")

app.include_router(HealthCheckController.router)
app.include_router(GeneralStatisticsController.router)

def main():
    return app