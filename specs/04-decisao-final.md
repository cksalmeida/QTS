# SPEC 04 — Decisão final e correções de auditoria

> **Tarefas do plano:** 4 e 5 (conclusão) — RN06, RN07 e achados de auditoria da SPEC 03
> **Executor:** Claude Code
> **Pré-leitura obrigatória:** `AGENTS.md` (seções 2 e 5 a 8) e `PRD.md` (seção 4, RN06, RN07 e seção 6)

---

## 1. Objetivo

Implementar `avaliar_credito`, que monta o motor completo usando as funções das
SPECs 02 e 03, e corrigir o achado de error guessing da auditoria da SPEC 03.
Ao final, a suíte passa inteira e a cobertura de `app/` continua em 100% de
linhas e ramificações.

## 2. Ordem de execução

Conforme a seção 2 do `AGENTS.md`, a mudança de regra vem **antes** do código:

1. Atualizar o `PRD.md` (seção 3).
2. Atualizar o `AGENTS.md` (seção 4).
3. Corrigir a validação (seção 5).
4. Implementar `avaliar_credito` (seção 6).
5. Escrever os testes (seção 7).

## 3. Atualização do PRD para a versão 1.1 (alteração autorizada)

Faça **somente** as alterações abaixo no `PRD.md`:

**3.1** No cabeçalho, troque `> **Versão:** 1.0` por `> **Versão:** 1.1`.

**3.2** Na seção 4 (Interface), logo após a lista de Enums, acrescente:

> `avaliar_credito` levanta `TypeError` se o argumento recebido não for uma
> `SolicitacaoCredito`.

**3.3** Na RN01, logo após a observação sobre `bool`, acrescente:

> Observação: inteiros grandes demais para serem convertidos em ponto flutuante
> (ex.: `10**400`) são tratados como não finitos e levantam `ValueError`.

**3.4** Na RN07, logo após a tabela, acrescente:

> Os cálculos das RN03 a RN05 só são executados quando nenhuma das regras 1 a 3
> se aplica. Assim, uma solicitação com score `MUITO_BAIXO` nunca chega a pedir
> taxa de juros.

**3.5** Na seção 7.3, acrescente ao final da lista de entradas: `inteiros
gigantes em campos numéricos (10**400)` e `objetos que não são
SolicitacaoCredito (None, dict) em avaliar_credito`.

**3.6** Na seção 9, acrescente a linha:

| Versão | Data | Descrição |
|---|---|---|
| 1.1 | 05/10/2026 | Achados de auditoria: inteiros gigantes tratados como não finitos; `avaliar_credito` valida o tipo do argumento; explicitado que as RN03 a RN05 só são calculadas após as regras 1 a 3 |

## 4. Atualização do AGENTS.md (alteração autorizada)

Na seção 8 ("Limites de atuação da IA"), acrescente ao final da lista:

> - Não crie, copie nem altere arquivos fora da pasta do projeto. A IA pode
>   **sugerir** sabotagens para a auditoria, mas a execução é feita pelo usuário.

Esta é a **única** alteração permitida no `AGENTS.md` nesta tarefa.

## 5. Correção da validação (achado da SPEC 03)

**Contexto:** `math.isfinite(10**400)` levanta `OverflowError`, uma exceção fora
do contrato da RN01 (que só prevê `TypeError` e `ValueError`).

**Correção:** em `_validar_campo_numerico`, capture o `OverflowError` gerado pela
checagem de finitude e levante no lugar
`ValueError("{campo} deve ser um número finito")`.

Não troque essa abordagem por "checar finitude só em `float`": nesse caso a renda
`10**400` seria aceita e geraria `OverflowError` mais tarde, no cálculo do
comprometimento.

## 6. Implementação de `avaliar_credito`

```python
def avaliar_credito(solicitacao: SolicitacaoCredito) -> ResultadoAnalise: ...
```

- Se `solicitacao` não for `SolicitacaoCredito`, levante
  `TypeError("solicitacao deve ser do tipo SolicitacaoCredito")`.
- Aplique as regras na **ordem exata** da tabela da RN07, retornando na primeira
  que se aplicar.
- Taxa, parcela e comprometimento só são calculados depois das regras 1 a 3
  (PRD v1.1), usando `obter_taxa_juros`, `calcular_parcela` e
  `calcular_comprometimento`. Não reimplemente esses cálculos.
- A elegibilidade por idade (RN06) pode ficar em uma função auxiliar privada.
- Docstring citando RN06 e RN07.

## 7. Testes (`tests/test_credito.py`)

Siga integralmente a seção 6 do `AGENTS.md`. Os valores esperados foram
calculados de forma independente a partir do PRD. Se algum teste falhar,
**não altere o esperado**: investigue, explique e reporte.

### 7.1 Novos casos no teste de valores não finitos (SPEC 03, seção 6.4)

| id | campo | valor | mensagem |
|---|---|---|---|
| `renda_inteiro_gigante` | `renda_mensal` | `10**400` | `"renda_mensal deve ser um número finito"` |
| `valor_inteiro_gigante` | `valor_solicitado` | `10**400` | `"valor_solicitado deve ser um número finito"` |

### 7.2 Decisão final — RN06 e RN07

Um teste parametrizado com `alteracoes` (um `dict`), `decisao` e `motivo`. A
solicitação é criada com `SolicitacaoCredito(**{**DADOS_VALIDOS, **alteracoes})`.
O teste verifica `resultado.decisao is decisao` **e** `resultado.motivo is motivo`.

Lembrete: `DADOS_VALIDOS` é o Exemplo 1 do PRD (renda 5000.00, score 750,
idade 30, valor 10000.00, 24 parcelas, sem restrição). Nele, a parcela é
R$ 596,67.

**Exemplos do PRD e regra 1**

| id | alteracoes | decisao | motivo |
|---|---|---|---|
| `decisao_exemplo_1_aprovado` | `{}` | `APROVADO` | `CRITERIOS_ATENDIDOS` |
| `decisao_exemplo_2_restricao` | `{"possui_restricao": True}` | `REPROVADO` | `RESTRICAO_CADASTRAL` |

**RN06 — elegibilidade por idade (regra 2)**

| id | alteracoes | decisao | motivo |
|---|---|---|---|
| `decisao_idade_0_valida_mas_nao_elegivel` | `{"idade": 0}` | `REPROVADO` | `IDADE_NAO_ELEGIVEL` |
| `decisao_idade_17_nao_elegivel` | `{"idade": 17}` | `REPROVADO` | `IDADE_NAO_ELEGIVEL` |
| `decisao_idade_18_elegivel` | `{"idade": 18}` | `APROVADO` | `CRITERIOS_ATENDIDOS` |
| `decisao_idade_75_elegivel` | `{"idade": 75}` | `APROVADO` | `CRITERIOS_ATENDIDOS` |
| `decisao_idade_76_nao_elegivel` | `{"idade": 76}` | `REPROVADO` | `IDADE_NAO_ELEGIVEL` |
| `decisao_idade_120_valida_mas_nao_elegivel` | `{"idade": 120}` | `REPROVADO` | `IDADE_NAO_ELEGIVEL` |

**Faixas de score (regras 3 e 5)**

| id | alteracoes | decisao | motivo |
|---|---|---|---|
| `decisao_score_299_insuficiente` | `{"score": 299}` | `REPROVADO` | `SCORE_INSUFICIENTE` |
| `decisao_score_300_analise_manual` | `{"score": 300}` | `ANALISE_MANUAL` | `SCORE_BAIXO` |
| `decisao_score_499_analise_manual` | `{"score": 499}` | `ANALISE_MANUAL` | `SCORE_BAIXO` |
| `decisao_score_500_aprovado` | `{"score": 500}` | `APROVADO` | `CRITERIOS_ATENDIDOS` |

**Limites de comprometimento (regras 4, 6 e 7)** — parcela de R$ 596,67, variando a renda

| id | alteracoes | comprometimento | decisao | motivo |
|---|---|---|---|---|
| `decisao_comprometimento_030_exato_aprovado` | `{"renda_mensal": 1988.90}` | 0,3000 | `APROVADO` | `CRITERIOS_ATENDIDOS` |
| `decisao_comprometimento_arredondado_030_aprovado` | `{"renda_mensal": 1988.88}` | 0,300003 → 0,3000 | `APROVADO` | `CRITERIOS_ATENDIDOS` |
| `decisao_comprometimento_03001_analise_manual` | `{"renda_mensal": 1988.24}` | 0,3001 | `ANALISE_MANUAL` | `COMPROMETIMENTO_ELEVADO` |
| `decisao_comprometimento_arredondado_035_analise_manual` | `{"renda_mensal": 1704.77}` | 0,3500003 → 0,3500 | `ANALISE_MANUAL` | `COMPROMETIMENTO_ELEVADO` |
| `decisao_comprometimento_03501_reprovado` | `{"renda_mensal": 1704.28}` | 0,3501 | `REPROVADO` | `COMPROMETIMENTO_EXCEDIDO` |

(A coluna de comprometimento é só explicativa; o teste verifica decisão e motivo.)

**Prioridade entre regras**

| id | alteracoes | decisao | motivo |
|---|---|---|---|
| `decisao_prioridade_restricao_sobre_idade_e_score` | `{"possui_restricao": True, "idade": 17, "score": 100}` | `REPROVADO` | `RESTRICAO_CADASTRAL` |
| `decisao_prioridade_idade_sobre_score` | `{"idade": 17, "score": 100}` | `REPROVADO` | `IDADE_NAO_ELEGIVEL` |
| `decisao_prioridade_score_insuficiente_sobre_comprometimento` | `{"score": 100, "renda_mensal": 100.00}` | `REPROVADO` | `SCORE_INSUFICIENTE` |
| `decisao_prioridade_excedido_sobre_score_baixo` | `{"score": 400, "renda_mensal": 2000.00}` | `REPROVADO` | `COMPROMETIMENTO_EXCEDIDO` |
| `decisao_prioridade_score_baixo_sobre_elevado` | `{"score": 400, "renda_mensal": 2700.00}` | `ANALISE_MANUAL` | `SCORE_BAIXO` |

**Extremo do produto**

| id | alteracoes | decisao | motivo |
|---|---|---|---|
| `decisao_valor_maximo_parcelas_minimas_aprovado` | `{"score": 650, "valor_solicitado": 50000.00, "num_parcelas": 6, "renda_mensal": 50000.00}` | `APROVADO` | `CRITERIOS_ATENDIDOS` |

### 7.3 Error guessing em `avaliar_credito`

Teste parametrizado esperando `TypeError` com
`match="solicitacao deve ser do tipo SolicitacaoCredito"`:

| id | argumento |
|---|---|
| `avaliar_none` | `None` |
| `avaliar_dict_com_dados_validos` | `dict(DADOS_VALIDOS)` |

## 8. Fora do escopo

- Qualquer alteração nas funções de cálculo.
- Alterações no `PRD.md` e no `AGENTS.md` além das seções 3 e 4 desta SPEC.
- Alterar `CLAUDE.md` ou `pyproject.toml`; adicionar dependências.
- Criar `README.md` ou `AI_USAGE.md` (serão escritos em outra etapa).

## 9. Critérios de aceitação

- [ ] `uv run pytest -v` passa com **103 testes** (76 anteriores + 2 da seção 7.1
      + 23 da seção 7.2 + 2 da seção 7.3).
- [ ] Cobertura de `app/credito.py` em 100%, sem nada em "Missing".
- [ ] `PRD.md` alterado somente conforme a seção 3; `AGENTS.md` somente conforme a seção 4.
- [ ] Nenhum `# pragma: no cover`, `skip` ou `xfail`.
- [ ] Nenhum arquivo criado ou alterado fora da pasta do projeto.

## 10. Relatório final

1. Arquivos alterados, com o diff do `PRD.md` e do `AGENTS.md`.
2. O código completo de `avaliar_credito`, de suas auxiliares e da nova versão
   de `_validar_campo_numerico`.
3. A saída completa de `uv run pytest -v`.
4. A saída do comando de cobertura.
5. Testes que falharam em execuções intermediárias: qual, por quê e como foi resolvido.
6. Desvios desta SPEC e o motivo.
7. Sugestão de mensagem de commit.
