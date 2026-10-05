"""Regras de negócio do motor de aprovação de crédito. Ver PRD.md."""

import math
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


def _validar_intervalo(campo: str, valor: float, minimo: float, maximo: float) -> None:
    """Exige que o valor esteja entre mínimo e máximo, inclusive (RN01)."""
    if not minimo <= valor <= maximo:
        raise ValueError(f"{campo} deve estar entre {minimo} e {maximo}")


def _validar_campo_inteiro(campo: str, valor: object, minimo: int, maximo: int) -> None:
    """Valida campo inteiro: tipo int (nunca bool) e depois intervalo (RN01)."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{campo} deve ser do tipo int")
    _validar_intervalo(campo, valor, minimo, maximo)


def _validar_campo_numerico(campo: str, valor: object) -> None:
    """Valida campo numérico: tipo int ou float (nunca bool) e finitude (RN01).

    Inteiros grandes demais para virar float (ex.: 10**400) são tratados como
    não finitos (RN01, PRD v1.1). O intervalo é validado à parte, pois varia
    entre os campos numéricos.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{campo} deve ser do tipo int ou float")
    try:
        finito = math.isfinite(valor)
    except OverflowError:
        finito = False
    if not finito:
        raise ValueError(f"{campo} deve ser um número finito")


@dataclass(frozen=True)
class SolicitacaoCredito:
    """Pedido de crédito e perfil do solicitante (PRD seção 4).

    Os campos são validados na criação do objeto, conforme a RN01: uma
    solicitação inválida levanta TypeError ou ValueError e nunca chega a existir.
    """

    renda_mensal: float
    score: int
    idade: int
    valor_solicitado: float
    num_parcelas: int
    possui_restricao: bool

    def __post_init__(self) -> None:
        """Valida os campos na ordem de declaração: tipo, finitude, intervalo (RN01)."""
        _validar_campo_numerico("renda_mensal", self.renda_mensal)
        if self.renda_mensal <= 0:
            raise ValueError("renda_mensal deve ser maior que zero")
        _validar_campo_inteiro("score", self.score, 0, 1000)
        _validar_campo_inteiro("idade", self.idade, 0, 120)
        _validar_campo_numerico("valor_solicitado", self.valor_solicitado)
        _validar_intervalo("valor_solicitado", self.valor_solicitado, 500, 50000)
        _validar_campo_inteiro("num_parcelas", self.num_parcelas, 6, 48)
        if not isinstance(self.possui_restricao, bool):
            raise TypeError("possui_restricao deve ser do tipo bool")


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


def _idade_elegivel(idade: int) -> bool:
    """Indica se a idade está entre 18 e 75 anos, inclusive (RN06).

    Pré-condição: idade já validada conforme RN01.
    """
    return 18 <= idade <= 75


def avaliar_credito(solicitacao: SolicitacaoCredito) -> ResultadoAnalise:
    """Decide o pedido de crédito aplicando as regras na ordem da RN07.

    Usa a elegibilidade por idade (RN06) e só calcula taxa, parcela e
    comprometimento (RN03 a RN05) depois das regras 1 a 3 (PRD v1.1).
    Levanta TypeError se o argumento não for uma SolicitacaoCredito.
    """
    if not isinstance(solicitacao, SolicitacaoCredito):
        raise TypeError("solicitacao deve ser do tipo SolicitacaoCredito")

    if solicitacao.possui_restricao:
        return ResultadoAnalise(Decisao.REPROVADO, Motivo.RESTRICAO_CADASTRAL)
    if not _idade_elegivel(solicitacao.idade):
        return ResultadoAnalise(Decisao.REPROVADO, Motivo.IDADE_NAO_ELEGIVEL)
    faixa = classificar_score(solicitacao.score)
    if faixa is FaixaScore.MUITO_BAIXO:
        return ResultadoAnalise(Decisao.REPROVADO, Motivo.SCORE_INSUFICIENTE)

    taxa = obter_taxa_juros(faixa)
    parcela = calcular_parcela(
        solicitacao.valor_solicitado, taxa, solicitacao.num_parcelas
    )
    comprometimento = calcular_comprometimento(parcela, solicitacao.renda_mensal)

    if comprometimento > 0.35:
        return ResultadoAnalise(Decisao.REPROVADO, Motivo.COMPROMETIMENTO_EXCEDIDO)
    if faixa is FaixaScore.BAIXO:
        return ResultadoAnalise(Decisao.ANALISE_MANUAL, Motivo.SCORE_BAIXO)
    if comprometimento > 0.30:
        return ResultadoAnalise(Decisao.ANALISE_MANUAL, Motivo.COMPROMETIMENTO_ELEVADO)
    return ResultadoAnalise(Decisao.APROVADO, Motivo.CRITERIOS_ATENDIDOS)
