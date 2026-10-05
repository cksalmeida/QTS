"""Regras de negócio do motor de aprovação de crédito. Ver PRD.md."""

from dataclasses import dataclass
from enum import Enum


class FaixaScore(Enum):
    """Faixas de score de crédito (PRD seção 4, RN02)."""

    MUITO_BAIXO = "MUITO_BAIXO"
    BAIXO = "BAIXO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


class Decisao(Enum):
    """Decisões possíveis da análise de crédito (PRD seção 4, RN07)."""

    APROVADO = "APROVADO"
    ANALISE_MANUAL = "ANALISE_MANUAL"
    REPROVADO = "REPROVADO"


class Motivo(Enum):
    """Motivos que justificam a decisão de crédito (PRD seção 4, RN07)."""

    RESTRICAO_CADASTRAL = "RESTRICAO_CADASTRAL"
    IDADE_NAO_ELEGIVEL = "IDADE_NAO_ELEGIVEL"
    SCORE_INSUFICIENTE = "SCORE_INSUFICIENTE"
    COMPROMETIMENTO_EXCEDIDO = "COMPROMETIMENTO_EXCEDIDO"
    SCORE_BAIXO = "SCORE_BAIXO"
    COMPROMETIMENTO_ELEVADO = "COMPROMETIMENTO_ELEVADO"
    CRITERIOS_ATENDIDOS = "CRITERIOS_ATENDIDOS"


@dataclass(frozen=True)
class SolicitacaoCredito:
    """Pedido de crédito e perfil do solicitante (PRD seção 4).

    A validação dos campos (RN01) ainda não está implementada.
    """

    renda_mensal: float
    score: int
    idade: int
    valor_solicitado: float
    num_parcelas: int
    possui_restricao: bool


@dataclass(frozen=True)
class ResultadoAnalise:
    """Resultado da análise de crédito: decisão e motivo (PRD seção 4, RN07)."""

    decisao: Decisao
    motivo: Motivo


_TAXAS_POR_FAIXA: dict[FaixaScore, float] = {
    FaixaScore.BAIXO: 0.045,
    FaixaScore.MEDIO: 0.030,
    FaixaScore.ALTO: 0.018,
}


def classificar_score(score: int) -> FaixaScore:
    """Classifica o score em faixas (RN02).

    Pré-condição: score já validado conforme RN01 (int entre 0 e 1000).
    """
    if score < 300:
        return FaixaScore.MUITO_BAIXO
    if score < 500:
        return FaixaScore.BAIXO
    if score < 700:
        return FaixaScore.MEDIO
    return FaixaScore.ALTO


def obter_taxa_juros(faixa: FaixaScore) -> float:
    """Retorna a taxa de juros mensal da faixa de score (RN03).

    Pré-condição: faixa é um membro de FaixaScore.
    Levanta ValueError para MUITO_BAIXO, que não possui taxa (RN03).
    """
    if faixa is FaixaScore.MUITO_BAIXO:
        raise ValueError("faixa MUITO_BAIXO não possui taxa de juros")
    return _TAXAS_POR_FAIXA[faixa]


def calcular_parcela(valor: float, taxa_mensal: float, num_parcelas: int) -> float:
    """Calcula a parcela com juros simples, arredondada a 2 casas (RN04).

    Pré-condição: valor e num_parcelas já validados conforme RN01 e
    taxa_mensal obtida conforme RN03.
    """
    valor_total = valor * (1 + taxa_mensal * num_parcelas)
    return round(valor_total / num_parcelas, 2)


def calcular_comprometimento(parcela: float, renda_mensal: float) -> float:
    """Calcula o comprometimento de renda, arredondado a 4 casas (RN05).

    Pré-condição: renda_mensal já validada conforme RN01 (maior que zero)
    e parcela calculada conforme RN04.
    """
    return round(parcela / renda_mensal, 4)
