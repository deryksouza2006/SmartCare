from datetime import date, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.main import app
from app.models import Prioridade, SmartCareRequest
from app.service import analisar_pet


def criar_request(
    dias_desde_atendimento: int,
    possui_proximo_agendamento: bool,
    possui_tratamento_registrado: bool,
    pet_id: int = 123,
) -> SmartCareRequest:
    return SmartCareRequest(
        petId=pet_id,
        dataUltimoAtendimento=date.today()
        - timedelta(days=dias_desde_atendimento),
        possuiProximoAgendamento=possui_proximo_agendamento,
        possuiTratamentoRegistrado=possui_tratamento_registrado,
    )


def test_tc01_baixa_prioridade() -> None:
    resultado = analisar_pet(criar_request(30, True, False))

    assert resultado.score == 0
    assert resultado.prioridade == Prioridade.BAIXA
    assert resultado.motivos == []


def test_tc02_media_prioridade() -> None:
    resultado = analisar_pet(criar_request(200, False, False))

    assert resultado.score == 50
    assert resultado.prioridade == Prioridade.MEDIA
    assert resultado.motivos == [
        "Mais de 180 dias desde o último atendimento",
        "Não possui próximo agendamento",
    ]


def test_tc03_alta_prioridade() -> None:
    resultado = analisar_pet(criar_request(400, False, True))

    assert resultado.score == 100
    assert resultado.prioridade == Prioridade.ALTA
    assert resultado.motivos == [
        "Longo período sem atendimento registrado",
        "Não possui próximo agendamento",
        "Existe tratamento registrado sem retorno agendado",
    ]


@pytest.mark.parametrize(
    ("dias", "score", "prioridade"),
    [
        (90, 0, Prioridade.BAIXA),
        (91, 10, Prioridade.BAIXA),
        (180, 10, Prioridade.BAIXA),
        (181, 30, Prioridade.MEDIA),
        (365, 30, Prioridade.MEDIA),
        (366, 60, Prioridade.ALTA),
    ],
)
def test_fronteiras_de_tempo(
    dias: int,
    score: int,
    prioridade: Prioridade,
) -> None:
    resultado = analisar_pet(criar_request(dias, True, False))

    assert resultado.score == score
    assert resultado.prioridade == prioridade


def test_score_nunca_ultrapassa_cem() -> None:
    resultado = analisar_pet(criar_request(10_000, False, True))

    assert resultado.score == 100
    assert resultado.score <= 100


def test_data_futura_e_rejeitada_pelo_modelo() -> None:
    with pytest.raises(ValidationError):
        SmartCareRequest(
            petId=123,
            dataUltimoAtendimento=date.today() + timedelta(days=1),
            possuiProximoAgendamento=True,
            possuiTratamentoRegistrado=False,
        )


def test_pet_id_deve_ser_positivo() -> None:
    with pytest.raises(ValidationError):
        SmartCareRequest(
            petId=0,
            dataUltimoAtendimento=date.today(),
            possuiProximoAgendamento=True,
            possuiTratamentoRegistrado=False,
        )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_health_check() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_endpoint_analisar() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/smartcare/analisar",
            json={
                "petId": 456,
                "dataUltimoAtendimento": (
                    date.today() - timedelta(days=200)
                ).isoformat(),
                "possuiProximoAgendamento": False,
                "possuiTratamentoRegistrado": False,
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "petId": 456,
        "score": 50,
        "prioridade": "MEDIA",
        "motivos": [
            "Mais de 180 dias desde o último atendimento",
            "Não possui próximo agendamento",
        ],
        "recomendacao": (
            "Revisar o acompanhamento do pet e avaliar necessidade de retorno"
        ),
    }


@pytest.mark.anyio
async def test_endpoint_rejeita_data_futura() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/smartcare/analisar",
            json={
                "petId": 123,
                "dataUltimoAtendimento": (
                    date.today() + timedelta(days=1)
                ).isoformat(),
                "possuiProximoAgendamento": True,
                "possuiTratamentoRegistrado": False,
            },
        )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_swagger_disponivel() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/docs")

    assert response.status_code == 200
