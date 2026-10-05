# SPEC 03 — Validação de entrada e ajuste de auditoria

> **Tarefas do plano:** 4 e 5 (parcial) — RN01, error guessing e correção apontada na auditoria da SPEC 02
> **Executor:** Claude Code
> **Pré-leitura obrigatória:** `AGENTS.md` (seções 5 a 8) e `PRD.md` (RN01 e seções 7.2 e 7.3)

---

## 1. Objetivo

Fazer a criação de `SolicitacaoCredito` validar todos os campos conforme a RN01,
de modo que uma solicitação inválida **nem chegue a existir**. Escrever os testes
de valores-limite e de error guessing dessa validação. Aplicar o ajuste de
auditoria da seção 5 desta SPEC.

Ao final, a suíte passa inteira e a cobertura de `app/` continua em 100% de
linhas e ramificações.

## 2. Onde a validação acontece

A validação fica no `__post_init__` de `SolicitacaoCredito` (que continua
`frozen=True`). As funções de cálculo da SPEC 02 **não mudam** e continuam com a
pré-condição documentada.

Atualize a docstring de `SolicitacaoCredito`: remova o aviso de que a RN01 ainda
não está implementada e informe que a validação ocorre na criação do objeto.

Para evitar regras duplicadas, use funções auxiliares privadas (prefixo `_`)
para validar campos inteiros e campos numéricos. O desenho dessas funções fica a
seu critério, desde que respeite as seções 3 e 4.

## 3. Regras de validação

### 3.1 Ordem

1. Os campos são validados **na ordem em que são declarados** na dataclass.
2. Para cada campo, a ordem é: **tipo** → **finitude** (só campos numéricos) →
   **intervalo**. A primeira violação encontrada levanta a exceção.

### 3.2 Regras por campo

| Campo | Tipo aceito | Finito | Intervalo |
|---|---|---|---|
| `renda_mensal` | `int` ou `float`, nunca `bool` | sim | `> 0` |
| `score` | `int`, nunca `bool` | — | `0` a `1000` |
| `idade` | `int`, nunca `bool` | — | `0` a `120` |
| `valor_solicitado` | `int` ou `float`, nunca `bool` | sim | `500` a `50000` |
| `num_parcelas` | `int`, nunca `bool` | — | `6` a `48` |
| `possui_restricao` | `bool` estritamente | — | — |

Todos os intervalos incluem os extremos, exceto `renda_mensal`, que exige ser
estritamente maior que zero.

## 4. Mensagens de erro

As mensagens são **padronizadas** e sempre começam pelo nome do campo:

| Situação | Exceção | Mensagem |
|---|---|---|
| Tipo inválido em campo `int` | `TypeError` | `"{campo} deve ser do tipo int"` |
| Tipo inválido em campo numérico | `TypeError` | `"{campo} deve ser do tipo int ou float"` |
| Tipo inválido em `possui_restricao` | `TypeError` | `"possui_restricao deve ser do tipo bool"` |
| `NaN` ou infinito | `ValueError` | `"{campo} deve ser um número finito"` |
| `renda_mensal <= 0` | `ValueError` | `"renda_mensal deve ser maior que zero"` |
| Fora do intervalo | `ValueError` | `"{campo} deve estar entre {mínimo} e {máximo}"` |

## 5. Ajuste de auditoria (achado da SPEC 02)

**Contexto:** a auditoria por sabotagem da SPEC 02 mostrou que a tolerância
padrão do `pytest.approx` é relativa e cresce com o valor. Para parcelas acima de
cerca de R$ 3.333, a remoção do arredondamento passaria despercebida.

**Ajustes:**

1. Em **todos** os testes existentes que usam `pytest.approx`, trocar para
   `pytest.approx(esperado, abs=1e-9)`.
2. Adicionar ao teste parametrizado de `calcular_parcela` o caso:

   | id | valor | taxa | parcelas | esperado |
   |---|---|---|---|---|
   | `parcela_valor_maximo_parcelas_minimas` | 50000.00 | 0.045 | 6 | 10583.33 |

3. **Alteração autorizada no `AGENTS.md`:** na seção 6, substitua a regra 8
   (`Comparações com float usam pytest.approx.`) por:

   > 8. Comparações com `float` usam `pytest.approx` com tolerância absoluta
   >    (`abs=1e-9`). A tolerância relativa padrão não é usada, porque cresce com
   >    o valor e pode esconder diferenças de centavos.

   Esta é a **única** alteração permitida no `AGENTS.md` nesta tarefa.

## 6. Testes (`tests/test_credito.py`)

Siga integralmente a seção 6 do `AGENTS.md`. Valores e ids devem ser usados
exatamente como estão. Se algum teste falhar, **não altere o esperado**:
investigue, explique e reporte.

### 6.1 Dados-base

Crie no topo do arquivo de testes uma constante `DADOS_VALIDOS` (um `dict`) com o
Exemplo 1 do PRD: renda 5000.00, score 750, idade 30, valor 10000.00,
24 parcelas, sem restrição.

Cada teste desta SPEC cria a solicitação alterando **um único campo**:
`SolicitacaoCredito(**{**DADOS_VALIDOS, campo: valor})`.

Use `DADOS_VALIDOS` também no teste de imutabilidade da SPEC 02, no lugar dos
valores escritos à mão.

### 6.2 Valores válidos nos limites — RN01 (BVA, lado válido)

Um teste parametrizado com `campo` e `valor`. A solicitação deve ser criada sem
erro e o campo deve guardar o valor informado.

| id | campo | valor |
|---|---|---|
| `renda_minima_valida_0_01` | `renda_mensal` | 0.01 |
| `renda_inteira_aceita` | `renda_mensal` | 5000 |
| `score_minimo_valido_0` | `score` | 0 |
| `score_maximo_valido_1000` | `score` | 1000 |
| `idade_minima_valida_0` | `idade` | 0 |
| `idade_maxima_valida_120` | `idade` | 120 |
| `valor_minimo_valido_500` | `valor_solicitado` | 500.00 |
| `valor_maximo_valido_50000` | `valor_solicitado` | 50000.00 |
| `valor_inteiro_aceito` | `valor_solicitado` | 10000 |
| `parcelas_minimo_valido_6` | `num_parcelas` | 6 |
| `parcelas_maximo_valido_48` | `num_parcelas` | 48 |
| `restricao_true_aceita` | `possui_restricao` | True |
| `restricao_false_aceita` | `possui_restricao` | False |

### 6.3 Valores fora do intervalo — RN01 (BVA, lado inválido)

Um teste parametrizado com `campo`, `valor` e `mensagem`. Espera `ValueError`
com `match=mensagem`.

| id | campo | valor | mensagem |
|---|---|---|---|
| `renda_zero` | `renda_mensal` | 0 | `"renda_mensal deve ser maior que zero"` |
| `renda_negativa` | `renda_mensal` | -100.00 | `"renda_mensal deve ser maior que zero"` |
| `score_abaixo_do_minimo` | `score` | -1 | `"score deve estar entre"` |
| `score_acima_do_maximo` | `score` | 1001 | `"score deve estar entre"` |
| `idade_abaixo_do_minimo` | `idade` | -1 | `"idade deve estar entre"` |
| `idade_acima_do_maximo` | `idade` | 121 | `"idade deve estar entre"` |
| `valor_abaixo_do_minimo` | `valor_solicitado` | 499.99 | `"valor_solicitado deve estar entre"` |
| `valor_acima_do_maximo` | `valor_solicitado` | 50000.01 | `"valor_solicitado deve estar entre"` |
| `parcelas_abaixo_do_minimo` | `num_parcelas` | 5 | `"num_parcelas deve estar entre"` |
| `parcelas_acima_do_maximo` | `num_parcelas` | 49 | `"num_parcelas deve estar entre"` |

### 6.4 Valores não finitos — error guessing (PRD 7.3)

Mesmo formato da 6.3, esperando `ValueError`.

| id | campo | valor | mensagem |
|---|---|---|---|
| `renda_nan` | `renda_mensal` | `float("nan")` | `"renda_mensal deve ser um número finito"` |
| `renda_infinita` | `renda_mensal` | `float("inf")` | `"renda_mensal deve ser um número finito"` |
| `renda_infinita_negativa` | `renda_mensal` | `float("-inf")` | `"renda_mensal deve ser um número finito"` |
| `valor_nan` | `valor_solicitado` | `float("nan")` | `"valor_solicitado deve ser um número finito"` |
| `valor_infinito` | `valor_solicitado` | `float("inf")` | `"valor_solicitado deve ser um número finito"` |

### 6.5 Tipos inválidos — error guessing (PRD 7.3)

Mesmo formato, esperando `TypeError`.

| id | campo | valor | mensagem |
|---|---|---|---|
| `renda_none` | `renda_mensal` | None | `"renda_mensal deve ser do tipo int ou float"` |
| `renda_texto` | `renda_mensal` | `"5000"` | `"renda_mensal deve ser do tipo int ou float"` |
| `renda_bool` | `renda_mensal` | True | `"renda_mensal deve ser do tipo int ou float"` |
| `score_none` | `score` | None | `"score deve ser do tipo int"` |
| `score_texto_fora_do_intervalo` | `score` | `"1001"` | `"score deve ser do tipo int"` |
| `score_bool` | `score` | True | `"score deve ser do tipo int"` |
| `score_float_inteiro` | `score` | 700.0 | `"score deve ser do tipo int"` |
| `idade_float` | `idade` | 30.0 | `"idade deve ser do tipo int"` |
| `idade_bool` | `idade` | False | `"idade deve ser do tipo int"` |
| `valor_texto` | `valor_solicitado` | `"10000"` | `"valor_solicitado deve ser do tipo int ou float"` |
| `valor_bool` | `valor_solicitado` | False | `"valor_solicitado deve ser do tipo int ou float"` |
| `parcelas_float` | `num_parcelas` | 24.0 | `"num_parcelas deve ser do tipo int"` |
| `parcelas_bool` | `num_parcelas` | True | `"num_parcelas deve ser do tipo int"` |
| `restricao_none` | `possui_restricao` | None | `"possui_restricao deve ser do tipo bool"` |
| `restricao_inteiro_1` | `possui_restricao` | 1 | `"possui_restricao deve ser do tipo bool"` |
| `restricao_texto_false` | `possui_restricao` | `"False"` | `"possui_restricao deve ser do tipo bool"` |

## 7. Fora do escopo

- `avaliar_credito`, RN06 e RN07 — SPEC 04.
- Qualquer mudança nas funções de cálculo além do previsto aqui.
- Alterar `PRD.md`, `CLAUDE.md` ou `pyproject.toml`.
- Adicionar dependências.

## 8. Critérios de aceitação

- [ ] `uv run pytest -v` passa com **76 testes** (31 da SPEC 02 + 1 novo caso de
      parcela + 13 + 10 + 5 + 16 desta SPEC).
- [ ] Cobertura de `app/credito.py` em 100%, sem nada em "Missing".
- [ ] Nenhum `pytest.approx` sem `abs=1e-9` no arquivo de testes.
- [ ] `AGENTS.md` alterado apenas na regra 8 da seção 6.
- [ ] Docstring de `SolicitacaoCredito` atualizada.
- [ ] Nenhum `# pragma: no cover`, `skip` ou `xfail`.

## 9. Relatório final

1. Arquivos alterados.
2. O código completo de `SolicitacaoCredito` e das funções auxiliares de validação.
3. A saída completa de `uv run pytest -v`.
4. A saída do comando de cobertura.
5. Testes que falharam em execuções intermediárias: qual, por quê e como foi resolvido.
6. Desvios desta SPEC e o motivo.
7. Sugestão de mensagem de commit.
