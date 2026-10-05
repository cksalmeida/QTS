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
    assert taxa == pytest.approx(esperado)


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
    ],
    ids=[
        "parcela_exemplo_1_do_prd",
        "parcela_taxa_medio",
        "parcela_taxa_baixo",
        "parcela_valor_minimo_parcelas_minimas",
        "parcela_valor_maximo_parcelas_maximas",
        "parcela_resultado_exato_sem_arredondamento",
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
    assert parcela == pytest.approx(esperado)


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
    assert comprometimento == pytest.approx(esperado)


@pytest.mark.unit
def test_solicitacao_credito_imutavel() -> None:
    """PRD seção 4 — SolicitacaoCredito é imutável (dataclass frozen)."""
    # Arrange
    solicitacao = SolicitacaoCredito(
        renda_mensal=5000.00,
        score=750,
        idade=30,
        valor_solicitado=10000.00,
        num_parcelas=24,
        possui_restricao=False,
    )

    # Act / Assert
    with pytest.raises(dataclasses.FrozenInstanceError, match="score"):
        solicitacao.score = 100  # type: ignore[misc]
