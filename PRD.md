# PRD — Motor de Aprovação de Crédito Pessoal

> **Versão:** 1.1
> **Autor:** Davi
> **Disciplina:** Qualidade e Teste de Software (QTS) — Atividade 1

---

## 1. Visão geral

Este documento especifica um **motor de decisão de crédito pessoal**: dado um pedido de empréstimo e o perfil do solicitante, o sistema decide se o crédito é **APROVADO**, **REPROVADO** ou enviado para **ANÁLISE MANUAL**, e informa o motivo da decisão.

Todas as regras são **determinísticas**: a mesma entrada sempre produz a mesma saída. O sistema não consulta data atual, serviços externos nem valores aleatórios.

## 2. Escopo

**Dentro do escopo**

- Validação dos dados de entrada.
- Classificação do score de crédito em faixas.
- Definição da taxa de juros conforme a faixa de score.
- Cálculo do valor da parcela e do comprometimento de renda.
- Decisão final com motivo.

**Fora do escopo**

- Persistência em banco de dados, interface gráfica ou API HTTP.
- Consulta a birôs de crédito (o score e a restrição são recebidos prontos).
- Contratação, assinatura ou liberação do dinheiro.

## 3. Glossário

| Termo | Significado |
|---|---|
| Score | Pontuação de crédito do solicitante, de 0 a 1000. Quanto maior, menor o risco. |
| Restrição cadastral | Indica se o solicitante está com o nome negativado. |
| Comprometimento de renda | Percentual da renda mensal consumido pela parcela (`parcela / renda`). |
| Análise manual | Pedido que não é aprovado nem reprovado automaticamente e segue para um analista humano. |

## 4. Interface

Módulo: `app/credito.py`

```python
def classificar_score(score: int) -> FaixaScore: ...
def obter_taxa_juros(faixa: FaixaScore) -> float: ...
def calcular_parcela(valor: float, taxa_mensal: float, num_parcelas: int) -> float: ...
def calcular_comprometimento(parcela: float, renda_mensal: float) -> float: ...
def avaliar_credito(solicitacao: SolicitacaoCredito) -> ResultadoAnalise: ...
```

**`SolicitacaoCredito`** (dataclass): `renda_mensal`, `score`, `idade`, `valor_solicitado`, `num_parcelas`, `possui_restricao`.

**`ResultadoAnalise`** (dataclass): `decisao: Decisao`, `motivo: Motivo`.

**Enums:**

- `FaixaScore`: `MUITO_BAIXO`, `BAIXO`, `MEDIO`, `ALTO`
- `Decisao`: `APROVADO`, `ANALISE_MANUAL`, `REPROVADO`
- `Motivo`: `RESTRICAO_CADASTRAL`, `IDADE_NAO_ELEGIVEL`, `SCORE_INSUFICIENTE`, `COMPROMETIMENTO_EXCEDIDO`, `SCORE_BAIXO`, `COMPROMETIMENTO_ELEVADO`, `CRITERIOS_ATENDIDOS`

`avaliar_credito` levanta `TypeError` se o argumento recebido não for uma `SolicitacaoCredito`.

## 5. Regras de negócio

### RN01 — Validação de entrada

Dados inválidos **não são uma decisão de crédito**: são erros e devem levantar exceção. Primeiro valida-se o **tipo** (`TypeError`), depois o **valor** (`ValueError`).

| Campo | Tipo aceito | Domínio válido | Erro se violado |
|---|---|---|---|
| `renda_mensal` | `int` ou `float` (não `bool`) | `> 0`, finito (sem `NaN`/`inf`) | `TypeError` / `ValueError` |
| `score` | `int` (não `bool`) | `0` a `1000` | `TypeError` / `ValueError` |
| `idade` | `int` (não `bool`) | `0` a `120` | `TypeError` / `ValueError` |
| `valor_solicitado` | `int` ou `float` (não `bool`) | `500,00` a `50.000,00`, finito | `TypeError` / `ValueError` |
| `num_parcelas` | `int` (não `bool`) | `6` a `48` | `TypeError` / `ValueError` |
| `possui_restricao` | `bool` | `True` ou `False` | `TypeError` |

> Observação: em Python, `bool` é subclasse de `int`. Por isso `True`/`False` devem ser rejeitados explicitamente nos campos numéricos.

> Observação: inteiros grandes demais para serem convertidos em ponto flutuante (ex.: `10**400`) são tratados como não finitos e levantam `ValueError`.

### RN02 — Faixas de score

| Score | Faixa |
|---|---|
| 0 a 299 | `MUITO_BAIXO` |
| 300 a 499 | `BAIXO` |
| 500 a 699 | `MEDIO` |
| 700 a 1000 | `ALTO` |

### RN03 — Taxa de juros mensal por faixa

| Faixa | Taxa mensal |
|---|---|
| `BAIXO` | 4,5% (`0.045`) |
| `MEDIO` | 3,0% (`0.030`) |
| `ALTO` | 1,8% (`0.018`) |
| `MUITO_BAIXO` | Não se aplica — levanta `ValueError` |

### RN04 — Cálculo da parcela (juros simples)

```
valor_total = valor_solicitado × (1 + taxa_mensal × num_parcelas)
parcela     = valor_total / num_parcelas
```

O resultado é **arredondado para 2 casas decimais**.

### RN05 — Comprometimento de renda

```
comprometimento = parcela / renda_mensal
```

O resultado é **arredondado para 4 casas decimais** antes de qualquer comparação, para evitar imprecisão de ponto flutuante nos limites.

### RN06 — Elegibilidade por idade

Somente solicitantes com idade **entre 18 e 75 anos (inclusive)** são elegíveis. Idade válida (RN01) porém fora dessa faixa resulta em `REPROVADO`.

### RN07 — Decisão final (ordem de avaliação)

As regras são avaliadas **na ordem abaixo**; a primeira que se aplicar define o resultado.

| # | Condição | Decisão | Motivo |
|---|---|---|---|
| 1 | `possui_restricao` é `True` | `REPROVADO` | `RESTRICAO_CADASTRAL` |
| 2 | idade `< 18` ou `> 75` | `REPROVADO` | `IDADE_NAO_ELEGIVEL` |
| 3 | faixa `MUITO_BAIXO` (score `< 300`) | `REPROVADO` | `SCORE_INSUFICIENTE` |
| 4 | comprometimento `> 0,35` | `REPROVADO` | `COMPROMETIMENTO_EXCEDIDO` |
| 5 | faixa `BAIXO` (score 300–499) | `ANALISE_MANUAL` | `SCORE_BAIXO` |
| 6 | comprometimento `> 0,30` (e `≤ 0,35`) | `ANALISE_MANUAL` | `COMPROMETIMENTO_ELEVADO` |
| 7 | nenhuma das anteriores | `APROVADO` | `CRITERIOS_ATENDIDOS` |

Os cálculos das RN03 a RN05 só são executados quando nenhuma das regras 1 a 3 se aplica. Assim, uma solicitação com score `MUITO_BAIXO` nunca chega a pedir taxa de juros.

## 6. Exemplos

**Exemplo 1 — Aprovado**
Renda R$ 5.000,00 · score 750 · idade 30 · valor R$ 10.000,00 · 24 parcelas · sem restrição
→ Faixa `ALTO`, taxa 1,8% → total R$ 14.320,00 → parcela **R$ 596,67** → comprometimento **0,1193**
→ **`APROVADO` / `CRITERIOS_ATENDIDOS`**

**Exemplo 2 — Reprovado por restrição**
Mesmo perfil do Exemplo 1, mas com `possui_restricao = True`
→ **`REPROVADO` / `RESTRICAO_CADASTRAL`** (regra 1 tem prioridade sobre todas as outras)

**Exemplo 3 — Entrada inválida**
`score = 1001` → **`ValueError`** (não há decisão de crédito)

## 7. Critérios de aceitação para testes

### 7.1 Partições de equivalência

| Variável | Partições |
|---|---|
| `score` | inválido negativo · `MUITO_BAIXO` · `BAIXO` · `MEDIO` · `ALTO` · inválido acima de 1000 |
| `idade` | inválida negativa · não elegível (< 18) · elegível (18–75) · não elegível (76–120) · inválida (> 120) |
| `comprometimento` | `≤ 0,30` · `> 0,30` e `≤ 0,35` · `> 0,35` |
| `possui_restricao` | `True` · `False` |

### 7.2 Valores-limite obrigatórios

| Variável | Valores a testar |
|---|---|
| `score` | -1, 0, 299, 300, 499, 500, 699, 700, 1000, 1001 |
| `idade` | -1, 0, 17, 18, 75, 76, 120, 121 |
| `valor_solicitado` | 499,99 · 500,00 · 50.000,00 · 50.000,01 |
| `num_parcelas` | 5, 6, 48, 49 |
| `renda_mensal` | 0 · 0,01 |
| `comprometimento` | 0,30 · 0,3001 · 0,35 · 0,3501 |

### 7.3 Error guessing (entradas inesperadas)

`None`, strings numéricas (`"5000"`), `True`/`False` em campos numéricos, `float("nan")`, `float("inf")`, `float` em campos inteiros (`score = 700.0`), `int` em `possui_restricao` (`1`), inteiros gigantes em campos numéricos (`10**400`), objetos que não são `SolicitacaoCredito` (`None`, `dict`) em `avaliar_credito`.

## 8. Requisitos não funcionais

- **RNF01:** Python 3.12+, projeto gerenciado com `uv` (`pyproject.toml`).
- **RNF02:** Todas as funções públicas com type hints.
- **RNF03:** Testes com Pytest, padrão AAA, marcados com `@pytest.mark.unit`.
- **RNF04:** Cobertura de **100% de linhas e ramificações** no pacote `app`, medida com `pytest-cov --cov-branch`.
- **RNF05:** Nenhuma regra de negócio pode depender de data/hora, aleatoriedade ou recursos externos.

## 9. Histórico de alterações

| Versão | Data | Descrição |
|---|---|---|
| 1.0 | 05/10/2026 | Versão inicial |
| 1.1 | 05/10/2026 | Achados de auditoria: inteiros gigantes tratados como não finitos; `avaliar_credito` valida o tipo do argumento; explicitado que as RN03 a RN05 só são calculadas após as regras 1 a 3 |
