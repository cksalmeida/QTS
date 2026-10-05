"""Testes unitários das regras de negócio do motor de crédito (ver PRD.md)."""

import dataclasses

import pytest

from app.credito import (
    FaixaScore,
    SolicitacaoCredito,
    calcular_comprometimento,
    calcular_parcela,
    classificar_score,
    obter_taxa_juros,
)

DADOS_VALIDOS = {
    "renda_mensal": 5000.00,
    "score": 750,
    "idade": 30,
    "valor_solicitado": 10000.00,
    "num_parcelas": 24,
    "possui_restricao": False,
}


@pytest.mark.unit
@pytest.mark.parametrize(
    ("score", "esperado"),
    [
        (0, FaixaScore.MUITO_BAIXO),
        (150, FaixaScore.MUITO_BAIXO),
        (299, FaixaScore.MUITO_BAIXO),
        (300, FaixaScore.BAIXO),
        (400, FaixaScore.BAIXO),
        (499, FaixaScore.BAIXO),
        (500, FaixaScore.MEDIO),
        (600, FaixaScore.MEDIO),
        (699, FaixaScore.MEDIO),
        (700, FaixaScore.ALTO),
        (850, FaixaScore.ALTO),
        (1000, FaixaScore.ALTO),
    ],
    ids=[
        "score_0_limite_inferior_muito_baixo",
        "score_150_representante_muito_baixo",
        "score_299_limite_superior_muito_baixo",
        "score_300_limite_inferior_baixo",
        "score_400_representante_baixo",
        "score_499_limite_superior_baixo",
        "score_500_limite_inferior_medio",
        "score_600_representante_medio",
        "score_699_limite_superior_medio",
        "score_700_limite_inferior_alto",
        "score_850_representante_alto",
        "score_1000_limite_superior_alto",
    ],
)
def test_classificar_score_faixas_e_limites(score: int, esperado: FaixaScore) -> None:
    """RN02 — partições e limites entre faixas de score."""
    # Arrange
    # (score e faixa esperada recebidos via parametrize)

    # Act
    faixa = classificar_score(score)

    # Assert
    assert faixa is esperado


@pytest.mark.unit
@pytest.mark.parametrize(
    ("faixa", "esperado"),
    [
        (FaixaScore.BAIXO, 0.045),
        (FaixaScore.MEDIO, 0.030),
        (FaixaScore.ALTO, 0.018),
    ],
    ids=[
        "taxa_faixa_baixo",
        "taxa_faixa_medio",
        "taxa_faixa_alto",
    ],
)
def test_obter_taxa_juros_por_faixa(faixa: FaixaScore, esperado: float) -> None:
    """RN03 — taxa de juros mensal de cada faixa com taxa definida."""
    # Arrange
    # (faixa e taxa esperada recebidas via parametrize)

    # Act
    taxa = obter_taxa_juros(faixa)

    # Assert
    assert taxa == pytest.approx(esperado, abs=1e-9)


@pytest.mark.unit
def test_obter_taxa_juros_muito_baixo_levanta_value_error() -> None:
    """RN03 — faixa MUITO_BAIXO não possui taxa e levanta ValueError."""
    # Arrange
    faixa = FaixaScore.MUITO_BAIXO

    # Act / Assert
    with pytest.raises(ValueError, match="MUITO_BAIXO"):
        obter_taxa_juros(faixa)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("valor", "taxa", "parcelas", "esperado"),
    [
        (10000.00, 0.018, 24, 596.67),
        (10000.00, 0.030, 24, 716.67),
        (10000.00, 0.045, 24, 866.67),
        (500.00, 0.018, 6, 92.33),
        (50000.00, 0.045, 48, 3291.67),
        (1200.00, 0.030, 12, 136.00),
        (50000.00, 0.045, 6, 10583.33),
    ],
    ids=[
        "parcela_exemplo_1_do_prd",
        "parcela_taxa_medio",
        "parcela_taxa_baixo",
        "parcela_valor_minimo_parcelas_minimas",
        "parcela_valor_maximo_parcelas_maximas",
        "parcela_resultado_exato_sem_arredondamento",
        "parcela_valor_maximo_parcelas_minimas",
    ],
)
def test_calcular_parcela_juros_simples(
    valor: float, taxa: float, parcelas: int, esperado: float
) -> None:
    """RN04 — parcela com juros simples arredondada a 2 casas."""
    # Arrange
    # (valor, taxa, parcelas e parcela esperada recebidos via parametrize)

    # Act
    parcela = calcular_parcela(valor, taxa, parcelas)

    # Assert
    assert parcela == pytest.approx(esperado, abs=1e-9)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("parcela", "renda", "esperado"),
    [
        (596.67, 5000.00, 0.1193),
        (1000.00, 3000.00, 0.3333),
        (1500.00, 5000.00, 0.3000),
        (1500.50, 5000.00, 0.3001),
        (1750.00, 5000.00, 0.3500),
        (1750.50, 5000.00, 0.3501),
        (1500.20, 5000.00, 0.3000),
        (1500.30, 5000.00, 0.3001),
    ],
    ids=[
        "comprometimento_exemplo_1_do_prd",
        "comprometimento_dizima_arredondada",
        "comprometimento_limite_exato_030",
        "comprometimento_logo_acima_de_030",
        "comprometimento_limite_exato_035",
        "comprometimento_logo_acima_de_035",
        "comprometimento_arredonda_para_baixo",
        "comprometimento_arredonda_para_cima",
    ],
)
def test_calcular_comprometimento_arredondado(
    parcela: float, renda: float, esperado: float
) -> None:
    """RN05 — comprometimento de renda arredondado a 4 casas."""
    # Arrange
    # (parcela, renda e comprometimento esperado recebidos via parametrize)

    # Act
    comprometimento = calcular_comprometimento(parcela, renda)

    # Assert
    assert comprometimento == pytest.approx(esperado, abs=1e-9)


@pytest.mark.unit
def test_solicitacao_credito_imutavel() -> None:
    """PRD seção 4 — SolicitacaoCredito é imutável (dataclass frozen)."""
    # Arrange
    solicitacao = SolicitacaoCredito(**DADOS_VALIDOS)

    # Act / Assert
    with pytest.raises(dataclasses.FrozenInstanceError, match="score"):
        solicitacao.score = 100  # type: ignore[misc]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("renda_mensal", 0.01),
        ("renda_mensal", 5000),
        ("score", 0),
        ("score", 1000),
        ("idade", 0),
        ("idade", 120),
        ("valor_solicitado", 500.00),
        ("valor_solicitado", 50000.00),
        ("valor_solicitado", 10000),
        ("num_parcelas", 6),
        ("num_parcelas", 48),
        ("possui_restricao", True),
        ("possui_restricao", False),
    ],
    ids=[
        "renda_minima_valida_0_01",
        "renda_inteira_aceita",
        "score_minimo_valido_0",
        "score_maximo_valido_1000",
        "idade_minima_valida_0",
        "idade_maxima_valida_120",
        "valor_minimo_valido_500",
        "valor_maximo_valido_50000",
        "valor_inteiro_aceito",
        "parcelas_minimo_valido_6",
        "parcelas_maximo_valido_48",
        "restricao_true_aceita",
        "restricao_false_aceita",
    ],
)
def test_solicitacao_credito_aceita_valores_limite_validos(
    campo: str, valor: float | int | bool
) -> None:
    """RN01 — valores nos limites do domínio válido são aceitos (BVA, lado válido)."""
    # Arrange
    dados = {**DADOS_VALIDOS, campo: valor}

    # Act
    solicitacao = SolicitacaoCredito(**dados)

    # Assert
    assert getattr(solicitacao, campo) is valor


@pytest.mark.unit
@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("renda_mensal", 0, "renda_mensal deve ser maior que zero"),
        ("renda_mensal", -100.00, "renda_mensal deve ser maior que zero"),
        ("score", -1, "score deve estar entre"),
        ("score", 1001, "score deve estar entre"),
        ("idade", -1, "idade deve estar entre"),
        ("idade", 121, "idade deve estar entre"),
        ("valor_solicitado", 499.99, "valor_solicitado deve estar entre"),
        ("valor_solicitado", 50000.01, "valor_solicitado deve estar entre"),
        ("num_parcelas", 5, "num_parcelas deve estar entre"),
        ("num_parcelas", 49, "num_parcelas deve estar entre"),
    ],
    ids=[
        "renda_zero",
        "renda_negativa",
        "score_abaixo_do_minimo",
        "score_acima_do_maximo",
        "idade_abaixo_do_minimo",
        "idade_acima_do_maximo",
        "valor_abaixo_do_minimo",
        "valor_acima_do_maximo",
        "parcelas_abaixo_do_minimo",
        "parcelas_acima_do_maximo",
    ],
)
def test_solicitacao_credito_fora_do_intervalo_levanta_value_error(
    campo: str, valor: float | int, mensagem: str
) -> None:
    """RN01 — valores fora do domínio válido levantam ValueError (BVA, lado inválido)."""
    # Arrange
    dados = {**DADOS_VALIDOS, campo: valor}

    # Act / Assert
    with pytest.raises(ValueError, match=mensagem):
        SolicitacaoCredito(**dados)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("renda_mensal", float("nan"), "renda_mensal deve ser um número finito"),
        ("renda_mensal", float("inf"), "renda_mensal deve ser um número finito"),
        ("renda_mensal", float("-inf"), "renda_mensal deve ser um número finito"),
        ("valor_solicitado", float("nan"), "valor_solicitado deve ser um número finito"),
        ("valor_solicitado", float("inf"), "valor_solicitado deve ser um número finito"),
    ],
    ids=[
        "renda_nan",
        "renda_infinita",
        "renda_infinita_negativa",
        "valor_nan",
        "valor_infinito",
    ],
)
def test_solicitacao_credito_nao_finito_levanta_value_error(
    campo: str, valor: float, mensagem: str
) -> None:
    """RN01 / PRD 7.3 — NaN e infinito levantam ValueError (error guessing)."""
    # Arrange
    dados = {**DADOS_VALIDOS, campo: valor}

    # Act / Assert
    with pytest.raises(ValueError, match=mensagem):
        SolicitacaoCredito(**dados)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("renda_mensal", None, "renda_mensal deve ser do tipo int ou float"),
        ("renda_mensal", "5000", "renda_mensal deve ser do tipo int ou float"),
        ("renda_mensal", True, "renda_mensal deve ser do tipo int ou float"),
        ("score", None, "score deve ser do tipo int"),
        ("score", "1001", "score deve ser do tipo int"),
        ("score", True, "score deve ser do tipo int"),
        ("score", 700.0, "score deve ser do tipo int"),
        ("idade", 30.0, "idade deve ser do tipo int"),
        ("idade", False, "idade deve ser do tipo int"),
        ("valor_solicitado", "10000", "valor_solicitado deve ser do tipo int ou float"),
        ("valor_solicitado", False, "valor_solicitado deve ser do tipo int ou float"),
        ("num_parcelas", 24.0, "num_parcelas deve ser do tipo int"),
        ("num_parcelas", True, "num_parcelas deve ser do tipo int"),
        ("possui_restricao", None, "possui_restricao deve ser do tipo bool"),
        ("possui_restricao", 1, "possui_restricao deve ser do tipo bool"),
        ("possui_restricao", "False", "possui_restricao deve ser do tipo bool"),
    ],
    ids=[
        "renda_none",
        "renda_texto",
        "renda_bool",
        "score_none",
        "score_texto_fora_do_intervalo",
        "score_bool",
        "score_float_inteiro",
        "idade_float",
        "idade_bool",
        "valor_texto",
        "valor_bool",
        "parcelas_float",
        "parcelas_bool",
        "restricao_none",
        "restricao_inteiro_1",
        "restricao_texto_false",
    ],
)
def test_solicitacao_credito_tipo_invalido_levanta_type_error(
    campo: str, valor: object, mensagem: str
) -> None:
    """RN01 / PRD 7.3 — tipos inválidos levantam TypeError (error guessing)."""
    # Arrange
    dados = {**DADOS_VALIDOS, campo: valor}

    # Act / Assert
    with pytest.raises(TypeError, match=mensagem):
        SolicitacaoCredito(**dados)
