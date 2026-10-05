# AGENTS.md — Regras de contexto para assistentes de IA

Este arquivo define como qualquer assistente de IA deve trabalhar neste repositório.
Ele vale para todas as ferramentas usadas no projeto (Claude no chat e Claude Code).

---

## 1. Sobre o projeto

Motor de aprovação de crédito pessoal em Python, desenvolvido para a Atividade 1 da
disciplina Qualidade e Teste de Software (QTS). O foco do projeto é **qualidade e
testabilidade**: regras determinísticas, validação defensiva e suíte de testes com
100% de cobertura de linhas e ramificações.

## 2. Fonte da verdade

- O arquivo `PRD.md` é a **única fonte da verdade** sobre as regras de negócio.
- Não invente regras, faixas, taxas ou limites que não estejam no `PRD.md`.
- Se um pedido do usuário conflitar com o `PRD.md`, ou se o PRD for ambíguo,
  **aponte o conflito e pergunte antes de agir**.
- Qualquer mudança de regra exige atualizar o `PRD.md` (incluindo a seção de
  histórico) **antes** de alterar código ou testes.

## 3. Stack e comandos

- Python **3.12+**, projeto gerenciado com **uv** (`pyproject.toml`).
- Nunca use `pip install` diretamente. Dependências entram com `uv add`
  (ou `uv add --dev` para ferramentas de teste).
- O pacote `app/` não pode ter dependências externas (apenas biblioteca padrão).

| Ação | Comando |
|---|---|
| Rodar testes | `uv run pytest -v` |
| Rodar só testes unitários | `uv run pytest -m unit -v` |
| Medir cobertura | `uv run pytest --cov=app --cov-branch --cov-report=term-missing` |

## 4. Estrutura do repositório

```
app/
  __init__.py
  credito.py          # regras de negócio (SUT)
tests/
  test_credito.py     # suíte de testes unitários
specs/                # especificações de tarefa executadas pela IA
PRD.md                # especificação
AGENTS.md             # este arquivo
CLAUDE.md             # ponte para o Claude Code (importa este arquivo)
AI_USAGE.md           # relatório de transparência do uso de IA
README.md
pyproject.toml
```

## 5. Regras para o código de negócio (`app/`)

1. **Type hints obrigatórios** em todos os parâmetros e retornos. Não use `Any`.
2. **Rastreabilidade:** toda função deve ter docstring citando a(s) regra(s) do PRD
   que implementa (ex.: `"""Classifica o score em faixas (RN02)."""`).
3. **Validação defensiva conforme RN01:**
   - validar o **tipo** primeiro (`TypeError`), depois o **valor** (`ValueError`);
   - rejeitar `bool` explicitamente em campos numéricos;
   - rejeitar `NaN` e `inf` em campos `float`;
   - mensagens de exceção em português, indicando o campo e o problema.
4. Use os `Enum` e `dataclass` definidos na seção 4 do PRD. Não use strings soltas
   para representar decisões, motivos ou faixas.
5. **Determinismo:** proibido usar data/hora atual, aleatoriedade, arquivos, rede ou
   variáveis de ambiente nas regras de negócio.
6. Funções pequenas, com uma responsabilidade cada. Siga a ordem de avaliação da
   RN07 exatamente como está no PRD.

## 6. Regras para os testes (`tests/`)

1. Todo teste segue o padrão **AAA**, com os comentários `# Arrange`, `# Act` e
   `# Assert` visíveis.
2. Todo teste recebe `@pytest.mark.unit`.
3. Use `@pytest.mark.parametrize` para Particionamento de Equivalência e Análise do
   Valor Limite, com `ids` descritivos (ex.: `"score_299_limite_superior_muito_baixo"`).
4. Cubra **todos** os valores-limite e casos de error guessing listados na
   seção 7 do PRD.
5. Nomeie os testes como `test_<funcao>_<cenario>`.
6. Cada teste (ou grupo parametrizado) indica no docstring a regra que verifica
   (ex.: `"""RN02 — limites entre faixas de score."""`).
7. Testes de decisão verificam **decisão e motivo**, não só a decisão.
8. Comparações com `float` usam `pytest.approx` com tolerância absoluta
   (`abs=1e-9`). A tolerância relativa padrão não é usada, porque cresce com
   o valor e pode esconder diferenças de centavos.
9. Testes de exceção usam `pytest.raises(..., match=...)` para conferir também a mensagem.
10. Testes não têm lógica própria (`if`, laços) e são independentes entre si.
11. Os **valores esperados** vêm do PRD, calculados de forma independente —
    nunca copiados da saída do próprio código.

## 7. Cobertura

- Meta: **100% de linhas e ramificações** no pacote `app`.
- É proibido usar `# pragma: no cover`, excluir arquivos da medição ou qualquer
  outro artifício para inflar a cobertura. A cobertura deve vir de testes reais.

## 8. Limites de atuação da IA (governança)

- **Nunca altere um valor esperado de teste só para ele passar.** Se um teste falhar,
  investigue se o erro está no código ou no teste, explique a causa e proponha a
  correção ao usuário.
- Não apague nem desative testes (`skip`, `xfail`) sem autorização explícita.
- Não adicione dependências sem autorização.
- Não altere o `PRD.md` sem pedido explícito.
- Antes de mudanças grandes (vários arquivos ou reestruturação), apresente o plano
  e aguarde aprovação.
- Ao concluir uma tarefa, faça um **resumo curto do que foi feito e do que o
  usuário deve revisar**, para registro no `AI_USAGE.md`.

## 9. Auditoria humana

Todo código e todo teste produzido com apoio de IA é revisado pelo autor do projeto
antes de ser commitado. A revisão inclui conferir valores esperados à mão contra o
PRD e introduzir defeitos propositais no código para confirmar que a suíte os detecta.
O processo é registrado no `AI_USAGE.md`.

## 10. Definição de pronto

Uma tarefa só está concluída quando:

- [ ] `uv run pytest -v` passa sem falhas;
- [ ] a cobertura de linhas e ramificações de `app/` está em 100%;
- [ ] o código respeita as seções 5 e 6 deste arquivo;
- [ ] o PRD e o código dizem a mesma coisa.
