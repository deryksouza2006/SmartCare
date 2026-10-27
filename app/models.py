from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, StrictBool, field_validator


class Prioridade(str, Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class SmartCareRequest(BaseModel):
    petId: int = Field(gt=0, strict=True)
    dataUltimoAtendimento: date
    possuiProximoAgendamento: StrictBool
    possuiTratamentoRegistrado: StrictBool

    @field_validator("dataUltimoAtendimento")
    @classmethod
    def validar_data_ultimo_atendimento(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("dataUltimoAtendimento não pode estar no futuro")

        return value


class SmartCareResponse(BaseModel):
    petId: int
    score: int = Field(ge=0, le=100)
    prioridade: Prioridade
    motivos: list[str]
    recomendacao: str


class HealthResponse(BaseModel):
    status: str
