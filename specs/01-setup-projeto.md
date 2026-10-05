# SPEC 01 — Setup do projeto

> **Tarefa do plano:** 3 — Criar e configurar o projeto
> **Executor:** Claude Code
> **Pré-leitura obrigatória:** `AGENTS.md` (regras gerais) e `PRD.md` seção 8 (requisitos não funcionais)

---

## 1. Objetivo

Deixar o esqueleto do projeto pronto e configurado com `uv`, **sem nenhuma regra de
negócio e sem nenhum teste**. Ao final, o Pytest deve conseguir rodar no projeto,
mesmo sem testes para coletar.

## 2. Passos

### 2.1 Verificar o `uv`

Rode `uv --version`. Se o `uv` não estiver instalado, **pare a execução** e informe
o usuário. Não instale o `uv` por conta própria.

### 2.2 Inicializar o projeto

Inicialize o projeto com `uv` **na pasta atual**, sem criar subpasta e **sem
sobrescrever** `PRD.md`, `AGENTS.md` e `CLAUDE.md`.

O `pyproject.toml` deve ter:

- `name = "motor-credito"`
- `description = "Motor de aprovação de crédito pessoal — Atividade 1 de QTS"`
- `requires-python = ">=3.12"`
- nenhuma dependência de produção

Fixe a versão do Python do projeto em 3.12 (arquivo `.python-version`).

Se o `uv init` gerar arquivos de exemplo (como `main.py` ou `hello.py`), remova-os.
Se gerar um `README.md`, mantenha-o apenas com o título `# Motor de Aprovação de
Crédito` — o conteúdo será escrito em outra tarefa.

### 2.3 Dependências de desenvolvimento

Adicione com `uv add --dev`:

- `pytest`
- `pytest-cov`

### 2.4 Configuração do Pytest

No `pyproject.toml`, crie a seção `[tool.pytest.ini_options]` com:

- `testpaths = ["tests"]`
- `pythonpath = ["."]` (para os testes importarem `app` sem instalar o pacote)
- `addopts = "--strict-markers"` (marcador digitado errado vira erro, não aviso)
- marcador `unit` registrado com a descrição `"testes unitários das regras de negócio"`

### 2.5 Estrutura de pastas

Crie:

- `app/__init__.py` — vazio
- `app/credito.py` — **apenas** uma docstring de módulo:
  `"""Regras de negócio do motor de aprovação de crédito. Ver PRD.md."""`
- `tests/` — pasta vazia, exceto por um arquivo `.gitkeep`
- `specs/` — se ainda não existir (esta SPEC deve estar dentro dela)

### 2.6 Git

- Se a pasta ainda não for um repositório Git, inicialize um.
- Garanta um `.gitignore` contendo pelo menos: `.venv/`, `__pycache__/`,
  `.pytest_cache/`, `.coverage`, `htmlcov/`.
- **Não faça commit.** O commit é feito pelo usuário após revisar.

### 2.7 Atualizar o AGENTS.md (alteração autorizada)

Na seção 4 do `AGENTS.md` ("Estrutura do repositório"), acrescente a linha:

```
specs/                # especificações de tarefa executadas pela IA
```

Esta é a **única** alteração permitida no `AGENTS.md` nesta tarefa.

## 3. Fora do escopo

- Implementar qualquer regra de negócio (enums, dataclasses, funções).
- Escrever qualquer teste.
- Alterar `PRD.md` ou `CLAUDE.md`.
- Instalar qualquer dependência além de `pytest` e `pytest-cov`.

## 4. Critérios de aceitação

- [ ] `uv run python --version` mostra Python 3.12 ou superior.
- [ ] `uv run pytest --collect-only` roda sem erro de configuração
      (é esperado que nenhum teste seja coletado).
- [ ] `uv run python -c "import app.credito"` roda sem erro.
- [ ] `pyproject.toml` contém exatamente o que pede a seção 2.2–2.4.
- [ ] `PRD.md` e `CLAUDE.md` estão inalterados; `AGENTS.md` só mudou na seção 4.

## 5. Relatório final

Ao terminar, apresente ao usuário:

1. A lista de arquivos criados, alterados e removidos.
2. O conteúdo completo do `pyproject.toml`.
3. A saída dos três comandos da seção 4.
4. Qualquer desvio desta SPEC e o motivo.
5. Uma sugestão de mensagem de commit.
