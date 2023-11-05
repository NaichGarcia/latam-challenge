from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from typing import List

from pydantic import BaseModel, validator

class FlightModel(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

    @validator("OPERA")
    def check_opera(cls, OPERA: str):
        airlines = ['Grupo LATAM', 'Sky Airline', 'Aerolineas Argentinas', 'Copa Air',
       'Latin American Wings', 'Avianca', 'JetSmart SPA', 'Gol Trans',
       'American Airlines', 'Air Canada', 'Iberia', 'Delta Air', 'Air France',
       'Aeromexico', 'United Airlines', 'Oceanair Linhas Aereas', 'Alitalia',
       'K.L.M.', 'British Airways', 'Qantas Airways', 'Lacsa', 'Austral',
       'Plus Ultra Lineas Aereas']
        
        OPERA_formatted = OPERA.capitalize()
        
        if(OPERA not in airlines):
            raise ValueError("Unknown airline")

        return OPERA
    
    @validator("TIPOVUELO")
    def check_tipovuelo(cls, TIPOVUELO: str):
        TIPOVUELO_formatted = TIPOVUELO.upper()

        if(TIPOVUELO_formatted != "N" and TIPOVUELO_formatted != "I"):
            raise ValueError("Unkown TIPOVUELO")
        
        return TIPOVUELO_formatted
        
    
    @validator("MES")
    def check_mes(cls, MES: int):
        if(MES < 1 or MES > 12):
            raise ValueError("MES out of range") 
           
        return MES
        

class FlightsModel(BaseModel):
    flights: List[FlightModel]

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        loc, msg = error["loc"], error["msg"]
        parameter = loc[-1]
        errors[parameter] = msg    

    return JSONResponse(
        status_code = status.HTTP_400_BAD_REQUEST,
        content = {
            "details": errors
        }
    )

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=200)
async def post_predict(flights_data: FlightsModel) -> dict:
    from challenge.model import DelayModel
    import pandas as pd

    # Input to DataFrame
    flights_list = [flight.dict() for flight in flights_data.flights]
    data = pd.DataFrame(flights_list)

    # Get dummy data for predictions
    model = DelayModel()
    features = model.get_dummies(data, ['OPERA', 'TIPOVUELO', 'MES'])

    
    # Prediction Simulation
    predicted_data = [0]
    # predicted_data = model.predict(features)

    output = {
        "predict": predicted_data
    }

    return output