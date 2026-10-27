from datetime import date

from app.models import Prioridade, SmartCareRequest, SmartCareResponse


RECOMENDACOES = {
    Prioridade.ALTA: "Entrar em contato com o tutor para retomar o acompanhamento",
    Prioridade.MEDIA: "Revisar o acompanhamento do pet e avaliar necessidade de retorno",
    Prioridade.BAIXA: "Manter acompanhamento conforme planejamento atual",
}


def _calcular_pontos_por_tempo(dias: int) -> tuple[int, str | None]:
    if dias <= 90:
        return 0, None
    if dias <= 180:
        return 10, "Mais de 90 dias desde o último atendimento"
    if dias <= 365:
        return 30, "Mais de 180 dias desde o último atendimento"

    return 60, "Longo período sem atendimento registrado"


def _definir_prioridade(score: int) -> Prioridade:
    if score <= 29:
        return Prioridade.BAIXA
    if score <= 59:
        return Prioridade.MEDIA

    return Prioridade.ALTA


def analisar_pet(
    request: SmartCareRequest,
    hoje: date | None = None,
) -> SmartCareResponse:
    data_referencia = hoje or date.today()
    dias_sem_atendimento = (
        data_referencia - request.dataUltimoAtendimento
    ).days

    if dias_sem_atendimento < 0:
        raise ValueError("dataUltimoAtendimento não pode estar no futuro")

    score, motivo_tempo = _calcular_pontos_por_tempo(dias_sem_atendimento)
    motivos: list[str] = []

    if motivo_tempo:
        motivos.append(motivo_tempo)

    if not request.possuiProximoAgendamento:
        score += 20
        motivos.append("Não possui próximo agendamento")

    if (
        request.possuiTratamentoRegistrado
        and not request.possuiProximoAgendamento
    ):
        score += 20
        motivos.append("Existe tratamento registrado sem retorno agendado")

    score = min(score, 100)
    prioridade = _definir_prioridade(score)

    return SmartCareResponse(
        petId=request.petId,
        score=score,
        prioridade=prioridade,
        motivos=motivos,
        recomendacao=RECOMENDACOES[prioridade],
    )
