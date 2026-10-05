# Motor de Aprovação de Crédito

Motor de decisão de crédito pessoal em Python, desenvolvido para a **Atividade 1** da
disciplina **Qualidade e Teste de Software (QTS)**: regras de negócio determinísticas,
validação defensiva, suíte de testes unitários com Pytest e 100% de cobertura de
linhas e ramificações.

**Autor:** Davi Mathais de Almeida

---

## O que o sistema faz

Recebe um pedido de empréstimo e o perfil do solicitante e devolve uma decisão com
o motivo:

| Decisão | Quando |
|---|---|
| `REPROVADO` | restrição cadastral, idade fora de 18–75 anos, score abaixo de 300 ou parcela acima de 35% da renda |
| `ANALISE_MANUAL` | score entre 300 e 499, ou parcela entre 30% e 35% da renda |
| `APROVADO` | nenhuma das situações acima |

As regras são avaliadas numa ordem fixa, e a primeira que se aplica define o
resultado. A especificação completa está no [`PRD.md`](PRD.md).

## Requisitos

- [uv](https://docs.astral.sh/uv/) (desenvolvido com a versão 0.12.5)
- Python 3.12 ou superior (o `uv` baixa automaticamente se necessário)

## Como rodar

```bash
git clone <url-do-repositório>
cd AT1-QTS
uv sync
```

**Testes:**

```bash
uv run pytest -v
```

**Somente os testes marcados como unitários:**

```bash
uv run pytest -m unit -v
```

**Cobertura de linhas e ramificações:**

```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing
```

## Exemplo de uso

```python
from app.credito import SolicitacaoCredito, avaliar_credito

solicitacao = SolicitacaoCredito(
    renda_mensal=5000.00,
    score=750,
    idade=30,
    valor_solicitado=10000.00,
    num_parcelas=24,
    possui_restricao=False,
)

print(avaliar_credito(solicitacao))
# ResultadoAnalise(decisao=<Decisao.APROVADO: 'APROVADO'>,
#                  motivo=<Motivo.CRITERIOS_ATENDIDOS: 'CRITERIOS_ATENDIDOS'>)
```

Dados inválidos não chegam a criar a solicitação: `SolicitacaoCredito(score=1001, ...)`
levanta `ValueError`, e `SolicitacaoCredito(score="750", ...)` levanta `TypeError`.

## Testes

São **103 testes**, todos com `@pytest.mark.unit`, organizados no padrão AAA e
parametrizados com `ids` descritivos:

| Técnica | Onde é aplicada |
|---|---|
| Particionamento de Equivalência | um representante de cada faixa de score, de cada decisão e de cada motivo |
| Análise do Valor Limite | limites de score, idade, valor, parcelas, renda e comprometimento, testados dos dois lados |
| Error Guessing | `None`, texto, `bool` em campos numéricos, `NaN`, infinito, inteiros gigantes, o texto `"False"` e objetos do tipo errado |
| Prioridade entre regras | combinações que disparariam duas regras ao mesmo tempo |

A suíte foi validada por auditoria com sabotagem: defeitos foram inseridos de
propósito no código para confirmar que os testes os detectam. Os detalhes estão no
[`AI_USAGE.md`](AI_USAGE.md).

## Estrutura

```
app/credito.py          regras de negócio
tests/test_credito.py   suíte de testes
PRD.md                  especificação das regras (v1.1)
AGENTS.md               regras de contexto para a IA
CLAUDE.md               ponte do Claude Code para o AGENTS.md
AI_USAGE.md             relatório de transparência do uso de IA
specs/                  especificações de tarefa executadas pela IA
```

## Uso de IA

O projeto foi desenvolvido com apoio do Claude (chat) e do Claude Code, sob as regras
do [`AGENTS.md`](AGENTS.md) e com auditoria humana em todas as etapas. O processo
completo está descrito no [`AI_USAGE.md`](AI_USAGE.md).
