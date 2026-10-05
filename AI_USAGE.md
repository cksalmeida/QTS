# AI_USAGE — Relatório de Transparência do Uso de IA

Este documento registra quais ferramentas de IA foram usadas no projeto, para quê,
e como todo o material produzido com apoio de IA foi auditado.

---

## 1. Ferramentas utilizadas

| Ferramenta | Onde | Papel no projeto |
|---|---|---|
| **Claude** (Chat, modelo Claude Opus 5.5) | Aplicativo | Planejamento: PRD, regras de contexto, SPEC's de cada tarefa, cálculo independente dos valores esperados e apoio na auditoria |
| **Claude Code** (modelo Claude Opus 5.5) | Terminal | Execução: Configuração do projeto, código e testes, sempre a partir de uma SPEC |

## 2. Fluxo de trabalho

O trabalho separou três papéis, para que nenhuma IA avaliasse o próprio trabalho:

```
Planejamento (Claude Chat)  →  Execução (Claude Code)  →  Auditoria (Autor + Claude Chat)
Escreve a SPEC                 Executa a SPEC             Confere, sabota, aceita ou rejeita
```

1. Cada tarefa foi descrita numa **SPEC** salva em `specs/`, com objetivo, passos,
   itens fora do escopo, critérios de aceitação e o relatório que a IA deveria entregar.
2. O Claude Code executou a SPEC e entregou o relatório, **sem fazer commit**.
3. O autor auditou o resultado (seção 5) e só então fez o commit.

## 3. Artefatos de governança

| Arquivo | Função |
|---|---|
| `PRD.md` | Única fonte da verdade sobre as regras de negócio. Mudanças de regra entram nele **antes** do código. |
| `AGENTS.md` | Contrato de atuação da IA: stack, regras de código e de testes, limites do que a IA pode fazer sozinha, definição de pronto. |
| `CLAUDE.md` | Ponte para o Claude Code: importa o `AGENTS.md`, mantendo uma única fonte de regras. |
| `specs/01` a `specs/04` | Registro exato do que foi pedido à IA em cada etapa. |

## 4. Como a IA foi empregada

| Etapa | O que a IA fez | O que o autor decidiu ou fez |
|---|---|---|
| Entendimento da atividade | Claude (chat) explicou os requisitos e conceitos | — |
| `PRD.md` | Claude (chat) redigiu a partir do domínio escolhido | Revisou as regras |
| `AGENTS.md` / `CLAUDE.md` | Claude (chat) redigiu | Revisou e adotou |
| SPEC 01 — setup | Claude Code configurou o projeto com `uv` | Avaliou os desvios relatados, conferiu `git status` e reexecutou os critérios |
| SPEC 02 — tipos e cálculos (RN02–RN05) | Claude Code implementou e testou | Auditoria por sabotagem; encontrou a fragilidade do `pytest.approx` |
| SPEC 03 — validação (RN01) | Claude Code implementou e testou | Revisou o código da validação; auditoria por sabotagem |
| SPEC 04 — decisão final (RN06–RN07) | Claude Code atualizou o PRD para v1.1, implementou e testou | Auditou também as sabotagens sugeridas pela IA |
| Valores esperados dos testes | Calculados no chat a partir das fórmulas do PRD, por um script independente do código do projeto, e escritos dentro das SPECs | Conferiu contas à mão |
| `AI_USAGE.md` e `README.md` | Rascunhos redigidos pelo Claude (chat) a partir do diário de bordo | Revisou e ajustou o texto |

**Regra central:** os valores esperados dos testes **nunca** foram obtidos a partir da
saída do próprio código. Se fossem, um código errado geraria testes igualmente errados.

## 5. Como foi feita a auditoria

### 5.1 Conferência de cada relatório

Cada relatório do Claude Code foi avaliado com três perguntas:

1. **A IA fez o que foi pedido?** Comparação item a item com a SPEC, incluindo a
   conferência dos totais de testes e de ramificações contra a estrutura esperada do
   código (ex.: 8 ramificações na SPEC 02 = 3 decisões em `classificar_score` + 1 em
   `obter_taxa_juros`, 2 caminhos cada).
2. **A IA fez algo que não foi pedido?** Cada desvio foi avaliado e aceito ou rejeitado.
3. **O relatório é verdadeiro?** O autor reexecutou `uv run pytest -v`, o comando de
   cobertura e `git status` no próprio terminal.

### 5.2 Auditoria por sabotagem

Testes que passam provam pouco sozinhos. Por isso, em cada SPEC o autor introduziu
defeitos propositais no código e verificou se a suíte os detectava. Para cada
sabotagem, a quantidade e os nomes dos testes que deveriam falhar foram **previstos
antes** da execução. O estado do código era preservado com `git add -A` e restaurado
com `git restore` após cada sabotagem.

**SPEC 02**

| Sabotagem | Previsto | Obtido |
|---|---|---|
| `score < 300` → `<= 300` | 1 | 1 |
| Comprometimento arredondado a 3 casas | 5 | 5 |
| Remoção do `round` da parcela | 5 | 5 |
| Remoção do `return` da parcela (feita por engano) | — | 6, defeito também detectado |

**SPEC 03**

| Sabotagem | Previsto | Obtido |
|---|---|---|
| Renda `<= 0` → `< 0` | 1 | 1 |
| Remoção apenas da checagem de `bool` | 2 | 2 (`renda_bool`: aceitação silenciosa; `valor_bool`: exceção errada) |
| Intervalo do valor validado antes da finitude | 4 | 4 |
| Remoção do `round` da parcela (após o ajuste do `approx`) | 6 | 6, incluindo o novo caso de R$ 10.583,33 |
| Remoção da validação de tipo inteira (feita por engano) | — | 3 na renda, defeito também detectado |

**SPEC 04**

| Sabotagem | Previsto | Obtido |
|---|---|---|
| Limites de idade exclusivos (`18 < idade < 75`) | 2 | 2 |
| Remoção do tratamento de `OverflowError` | 2 | 2, com o bug original de volta |
| Regras 4 e 5 da RN07 invertidas | 1 | 1 |
| Taxa calculada antes da regra 3 | 2 | 2 |
| `comprometimento > 0.30` → `>= 0.30` | 2 (a IA previu 1) | 2 |
| `comprometimento > 0.35` → `>= 0.35` | 1 | 1 |
| Remoção do `round` do comprometimento | 6 | 6, incluindo duas decisões de crédito alteradas |

Em algumas rodadas as sabotagens foram aplicadas ao mesmo tempo. Quando isso fez dois
defeitos atingirem o mesmo teste, impedindo saber qual deles foi detectado, as
sabotagens envolvidas foram refeitas individualmente.

## 6. Achados da auditoria

| # | Achado | Como foi encontrado | Tratamento |
|---|---|---|---|
| 1 | A tolerância padrão do `pytest.approx` é relativa e cresce com o valor; acima de cerca de R$ 3.333, a falta de arredondamento em centavos passaria despercebida | Sabotagem da SPEC 02: o caso de R$ 3.291,67 falhou por margem mínima | SPEC 03: `approx` com `abs=1e-9`, novo caso de parcela alta e atualização da regra 8 da seção 6 do `AGENTS.md` |
| 2 | `math.isfinite(10**400)` levanta `OverflowError`, exceção fora do contrato da RN01 | Error guessing durante a revisão da SPEC 03 | `PRD.md` v1.1 e correção na SPEC 04, com dois novos testes |
| 3 | O Claude Code executou sabotagens por iniciativa própria numa cópia fora da pasta do projeto, sem listar isso como desvio | Leitura do relatório da SPEC 03 | Nova regra na seção 8 do `AGENTS.md`; na SPEC 04 a IA passou a apenas sugerir sabotagens |
| 4 | A previsão da IA para a sabotagem `>= 0.30` estava incompleta (indicava 1 falha; o correto eram 2, pois o comprometimento de 0,300003 também é arredondado para 0,30) | Previsão independente feita no chat e confirmada com a sabotagem isolada | Registrado como evidência de que sugestões da IA também precisam de auditoria |
| 5 | Sem o `match` nos testes de exceção, a remoção da validação de tipo passaria despercebida para `None` e texto, pois o próprio Python também levanta `TypeError` | Sabotagem da SPEC 03 | Confirmou a regra 9 da seção 6 do `AGENTS.md` (exceções sempre com `match`) |

## 7. Decisões tomadas pelo autor

- Escolha do domínio e regras do PRD.
- Aceitação ou rejeição de cada desvio relatado pela IA (ex.: uso de `uv init --bare`
  aceito; criação antecipada do `README.md` adiada para manter o escopo).
- Inclusão das correções de auditoria nas SPECs seguintes.
- Todos os commits, feitos manualmente após a auditoria de cada etapa.

## 8. Limitações e aprendizados

- **100% de cobertura não garante testes bons.** A cobertura de ramificações não
  verifica os dois lados de um `or` nem de uma comparação encadeada como
  `18 <= idade <= 75`. Esses casos foram protegidos por testes de limite específicos.
- **A IA errou de formas sutis.** Agiu fora do escopo uma vez e fez uma previsão
  incompleta, o que reforça a necessidade de revisão humana.
- **A governança evoluiu com o projeto.** O `AGENTS.md` recebeu duas regras novas e o
  `PRD.md` uma nova versão, ambos motivados por achados da auditoria.
