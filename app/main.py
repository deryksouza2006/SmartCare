from fastapi import FastAPI

from app.models import HealthResponse, SmartCareRequest, SmartCareResponse
from app.service import analisar_pet


app = FastAPI(
    title="PetJourney SmartCare API",
    description="Motor de priorização de acompanhamento de pets.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/smartcare/analisar", response_model=SmartCareResponse)
def analisar(request: SmartCareRequest) -> SmartCareResponse:
    return analisar_pet(request)
