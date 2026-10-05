# SPEC 02 — Tipos e funções de cálculo

> **Tarefas do plano:** 4 e 5 (parcial) — implementação e testes das regras RN02 a RN05
> **Executor:** Claude Code
> **Pré-leitura obrigatória:** `AGENTS.md` (seções 5 a 8) e `PRD.md` (seções 4 e 5, RN02 a RN05)

---

## 1. Objetivo

Implementar em `app/credito.py` os tipos do domínio e as quatro funções de cálculo,
e escrever em `tests/test_credito.py` os testes dessas funções. Ao final, a suíte
passa inteira e a cobertura de `app/` é de 100% de linhas e ramificações.

## 2. Decisão de projeto: validação na fronteira

A validação de entrada (RN01) **não faz parte desta SPEC**. Ela será implementada
na SPEC 03, centralizada na criação de `SolicitacaoCredito`.

Nesta SPEC, as funções de cálculo **assumem entradas já válidas** conforme RN01 e
não fazem checagem de tipo nem de faixa. Isso deve estar escrito na docstring de
cada uma (ex.: `"Pré-condição: score já validado conforme RN01."`).

A única exceção é a regra explícita da RN03: `obter_taxa_juros(FaixaScore.MUITO_BAIXO)`
levanta `ValueError`.

## 3. Implementação (`app/credito.py`)

### 3.1 Enums

Crie `FaixaScore`, `Decisao` e `Motivo` como `Enum`, com os membros exatamente como
na seção 4 do PRD. O valor de cada membro é o próprio nome em texto
(ex.: `APROVADO = "APROVADO"`).

### 3.2 Dataclasses

Crie ambas com `@dataclass(frozen=True)` (imutáveis):

- `SolicitacaoCredito` com os campos `renda_mensal: float`, `score: int`,
  `idade: int`, `valor_solicitado: float`, `num_parcelas: int`,
  `possui_restricao: bool` — **sem validação nesta SPEC**.
- `ResultadoAnalise` com os campos `decisao: Decisao` e `motivo: Motivo`.

### 3.3 Funções

| Função | Regra | Comportamento |
|---|---|---|
| `classificar_score(score: int) -> FaixaScore` | RN02 | faixas conforme a tabela da RN02 |
| `obter_taxa_juros(faixa: FaixaScore) -> float` | RN03 | taxas conforme a tabela da RN03; `MUITO_BAIXO` levanta `ValueError` com a mensagem `"faixa MUITO_BAIXO não possui taxa de juros"` |
| `calcular_parcela(valor: float, taxa_mensal: float, num_parcelas: int) -> float` | RN04 | juros simples, arredondado para 2 casas com `round` |
| `calcular_comprometimento(parcela: float, renda_mensal: float) -> float` | RN05 | `parcela / renda_mensal`, arredondado para 4 casas com `round` |

**Não crie** `avaliar_credito` nesta SPEC.

## 4. Testes (`tests/test_credito.py`)

Siga integralmente a seção 6 do `AGENTS.md`. Os **valores esperados abaixo foram
calculados de forma independente a partir do PRD** e devem ser usados exatamente
como estão. Se algum teste falhar, **não altere o valor esperado**: investigue,
explique a causa e reporte (AGENTS.md, seção 8).

Remova `tests/.gitkeep`, pois a pasta deixará de estar vazia.

### 4.1 `classificar_score` — RN02 (EP + BVA)

Um único teste parametrizado com os casos:

| id | score | esperado |
|---|---|---|
| `score_0_limite_inferior_muito_baixo` | 0 | `MUITO_BAIXO` |
| `score_150_representante_muito_baixo` | 150 | `MUITO_BAIXO` |
| `score_299_limite_superior_muito_baixo` | 299 | `MUITO_BAIXO` |
| `score_300_limite_inferior_baixo` | 300 | `BAIXO` |
| `score_400_representante_baixo` | 400 | `BAIXO` |
| `score_499_limite_superior_baixo` | 499 | `BAIXO` |
| `score_500_limite_inferior_medio` | 500 | `MEDIO` |
| `score_600_representante_medio` | 600 | `MEDIO` |
| `score_699_limite_superior_medio` | 699 | `MEDIO` |
| `score_700_limite_inferior_alto` | 700 | `ALTO` |
| `score_850_representante_alto` | 850 | `ALTO` |
| `score_1000_limite_superior_alto` | 1000 | `ALTO` |

### 4.2 `obter_taxa_juros` — RN03

Teste parametrizado (comparar com `pytest.approx`):

| id | faixa | esperado |
|---|---|---|
| `taxa_faixa_baixo` | `BAIXO` | 0.045 |
| `taxa_faixa_medio` | `MEDIO` | 0.030 |
| `taxa_faixa_alto` | `ALTO` | 0.018 |

Teste separado: `MUITO_BAIXO` levanta `ValueError` com `match="MUITO_BAIXO"`.

### 4.3 `calcular_parcela` — RN04

Teste parametrizado (comparar com `pytest.approx`):

| id | valor | taxa | parcelas | esperado |
|---|---|---|---|---|
| `parcela_exemplo_1_do_prd` | 10000.00 | 0.018 | 24 | 596.67 |
| `parcela_taxa_medio` | 10000.00 | 0.030 | 24 | 716.67 |
| `parcela_taxa_baixo` | 10000.00 | 0.045 | 24 | 866.67 |
| `parcela_valor_minimo_parcelas_minimas` | 500.00 | 0.018 | 6 | 92.33 |
| `parcela_valor_maximo_parcelas_maximas` | 50000.00 | 0.045 | 48 | 3291.67 |
| `parcela_resultado_exato_sem_arredondamento` | 1200.00 | 0.030 | 12 | 136.00 |

### 4.4 `calcular_comprometimento` — RN05

Teste parametrizado (comparar com `pytest.approx`):

| id | parcela | renda | esperado |
|---|---|---|---|
| `comprometimento_exemplo_1_do_prd` | 596.67 | 5000.00 | 0.1193 |
| `comprometimento_dizima_arredondada` | 1000.00 | 3000.00 | 0.3333 |
| `comprometimento_limite_exato_030` | 1500.00 | 5000.00 | 0.3000 |
| `comprometimento_logo_acima_de_030` | 1500.50 | 5000.00 | 0.3001 |
| `comprometimento_limite_exato_035` | 1750.00 | 5000.00 | 0.3500 |
| `comprometimento_logo_acima_de_035` | 1750.50 | 5000.00 | 0.3501 |
| `comprometimento_arredonda_para_baixo` | 1500.20 | 5000.00 | 0.3000 |
| `comprometimento_arredonda_para_cima` | 1500.30 | 5000.00 | 0.3001 |

### 4.5 Imutabilidade das dataclasses

Um teste que cria uma `SolicitacaoCredito` válida e confirma que alterar um campo
levanta `dataclasses.FrozenInstanceError`. Use como dados o Exemplo 1 do PRD
(renda 5000.00, score 750, idade 30, valor 10000.00, 24 parcelas, sem restrição).

## 5. Fora do escopo

- Validação de entrada (RN01) e testes de error guessing — SPEC 03.
- `avaliar_credito`, RN06 e RN07 — SPEC 04.
- Alterar `PRD.md`, `AGENTS.md`, `CLAUDE.md` ou `pyproject.toml`.
- Adicionar dependências.

## 6. Critérios de aceitação

- [ ] `uv run pytest -v` passa com todos os testes das seções 4.1 a 4.5.
- [ ] `uv run pytest --cov=app --cov-branch --cov-report=term-missing` mostra
      100% em `app/credito.py`, sem linhas ou ramificações listadas em "Missing".
- [ ] Todo teste tem `@pytest.mark.unit`, comentários AAA e docstring citando a RN.
- [ ] Toda função tem type hints e docstring citando a RN e a pré-condição.
- [ ] Nenhum `# pragma: no cover`, `skip` ou `xfail`.

## 7. Relatório final

Ao terminar, apresente ao usuário:

1. Arquivos criados, alterados e removidos.
2. A saída completa de `uv run pytest -v`.
3. A saída do comando de cobertura.
4. **Se algum teste falhou em alguma execução intermediária**: qual, por quê e
   como foi resolvido (código corrigido ou dúvida levada ao usuário).
5. Qualquer desvio desta SPEC e o motivo.
6. Uma sugestão de mensagem de commit.
