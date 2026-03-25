# LinkedIn RPA

Automação do LinkedIn para envio de convites de conexão e candidatura a vagas via Easy Apply, com avaliação inteligente usando Claude AI.

## Funcionalidades

- **Conexões**: envia convites automaticamente para pessoas em uma busca do LinkedIn
- **Candidaturas**: avalia vagas com base no seu currículo e se candidata via Easy Apply
  - Avalia idioma da vaga (apenas pt-BR)
  - Respeita nível de senioridade desejado
  - Estima pretensão salarial com base na vaga e no mercado
  - Responde perguntas customizadas do formulário usando IA
  - Registra vagas já candidatadas para não repetir

## Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes)
- Google Chrome instalado
- Conta no LinkedIn (já logada no Chrome)
- Claude Code com plano Pro ativo (usado pela IA de avaliação)

## Instalação

```bash
git clone https://github.com/SrMarinho/linkedin-rpa.git
cd linkedin-rpa
uv sync
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
HEADLESS=FALSE
```

> Defina `HEADLESS=TRUE` para rodar o Chrome em segundo plano (sem janela visível).

## Uso

### Enviar convites de conexão

```bash
uv run python main.py connect --url "URL_DA_BUSCA_DE_PESSOAS"
```

**Parâmetros:**

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--url` | Sim | URL da busca de pessoas do LinkedIn |
| `--max-pages` | Não | Limite de páginas (padrão: 100) |

**Exemplo:**
```bash
uv run python main.py connect \
  --url "https://www.linkedin.com/search/results/people/?keywords=recrutador&network=%5B%22F%22%5D"
```

---

### Candidatar a vagas

```bash
uv run python main.py apply --url "URL_DA_BUSCA_DE_VAGAS" --resume "caminho/para/curriculo.pdf"
```

**Parâmetros:**

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--url` | Sim | URL da busca de vagas do LinkedIn (com filtro Easy Apply ativo) |
| `--resume` | Não | Caminho para o currículo em PDF ou TXT (padrão: `resume.txt`) |
| `--preferences` | Não | Preferências para guiar a avaliação |
| `--level` | Não | Nível de senioridade desejado: `junior`, `pleno`, `senior` |
| `--max-pages` | Não | Limite de páginas (padrão: 100) |

**Exemplo:**
```bash
uv run python main.py apply \
  --url "https://www.linkedin.com/jobs/search/?keywords=desenvolvedor+python&f_AL=true" \
  --resume "C:/Users/seu_usuario/Downloads/Curriculo.pdf" \
  --preferences "prefiro vagas backend, Python, remoto" \
  --level junior
```

> **Dica:** Use o filtro **"Candidatura simplificada"** (`f_AL=true`) na URL para garantir que só apareçam vagas com Easy Apply.

---

## Como funciona o fluxo de candidatura

```
Para cada vaga encontrada:
  1. Verifica se já se candidatou anteriormente (applied_jobs.json)
  2. Avalia com IA:
     - Idioma da vaga (apenas pt-BR)
     - Nível de senioridade (se --level informado)
     - Fit técnico com o currículo
     - Alinhamento com as preferências
  3. Se aprovada:
     - Estima a pretensão salarial com base na vaga e no mercado
     - Clica em "Candidatura simplificada"
     - Preenche o formulário (salário, perguntas customizadas via IA)
     - Envia a candidatura
     - Salva em applied_jobs.json
```

## Arquivos locais gerados

| Arquivo | Descrição |
|---------|-----------|
| `applied_jobs.json` | Registro de todas as candidaturas enviadas |
| `screenshots.png` | Screenshot tirado ao final da execução |

> Esses arquivos estão no `.gitignore` e não são enviados ao repositório.

## Estrutura do projeto

```
linkedin_rpa/
├── main.py                              # Ponto de entrada e CLI
├── src/
│   ├── automation/
│   │   ├── pages/
│   │   │   ├── linkedin_search_page.py  # Page object da busca de pessoas
│   │   │   └── jobs_search_page.py      # Page object da busca de vagas
│   │   └── tasks/
│   │       ├── connection_manager.py        # Orquestra envio de conexões
│   │       └── job_application_manager.py   # Orquestra candidaturas
│   └── core/
│       └── use_cases/
│           ├── job_evaluator.py             # Avalia fit da vaga com IA
│           ├── salary_estimator.py          # Estima pretensão salarial com IA
│           ├── job_application_handler.py   # Preenche e envia o Easy Apply
│           └── applied_jobs_tracker.py      # Persiste candidaturas enviadas
```
