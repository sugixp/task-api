# Task API

API REST para gerenciamento de tarefas, com autenticação de usuários, construída como projeto de estudo aplicado, cobrindo o ciclo completo de desenvolvimento: back-end, testes automatizados, containerização, deploy em nuvem e front-end de consumo.

🔗 **Front-end (GitHub Pages):** https://sugixp.github.io/task-api/

> ⚠️ **Sobre o deploy na AWS:** a API foi implantada e testada com sucesso no AWS Elastic Beanstalk (evidências e passo a passo neste README). O ambiente foi encerrado propositalmente após a validação para evitar custos de manutenção contínua fora do escopo deste projeto de estudo. A reativação é rápida — o ambiente inteiro é recriado com um único comando (`eb create task-api-env`), já que toda a configuração permanece salva no projeto.

## Sobre o projeto

Este projeto evoluiu a partir de um CRUD simples em Python/SQLite para uma API mais robusta, com o objetivo de demonstrar na prática conceitos usados em ambientes profissionais: autenticação segura, isolamento de dados por usuário, testes automatizados, containerização e deploy em nuvem.

## Tecnologias utilizadas

- **Python 3** — linguagem principal
- **FastAPI** — framework web para construção da API
- **SQLAlchemy** — ORM para modelagem e acesso ao banco de dados
- **SQLite** — banco de dados relacional
- **Pydantic** — validação de dados de entrada e saída
- **JWT (python-jose)** — autenticação baseada em token
- **Passlib + bcrypt** — hash seguro de senhas
- **Pytest** — testes automatizados
- **Docker** — containerização da aplicação
- **AWS Elastic Beanstalk** — deploy e hospedagem em nuvem
- **HTML, CSS e JavaScript** — front-end de consumo da API

## Funcionalidades

- Cadastro e login de usuários, com senha protegida por hash
- Autenticação via token JWT
- CRUD completo de tarefas (criar, listar, atualizar, remover)
- Cada usuário só acessa suas próprias tarefas (isolamento por autenticação)
- Documentação interativa automática (Swagger) em `/docs`
- Testes automatizados cobrindo os principais fluxos (sucesso e erro)
- Front-end simples para demonstrar o consumo real da API

## Estrutura do projeto

```
task-api/
├── main.py              # Rotas da API
├── models.py             # Modelos de dados (SQLAlchemy)
├── database.py            # Configuração de conexão com o banco
├── auth.py               # Lógica de hash de senha e geração de token JWT
├── test_main.py            # Testes automatizados (pytest)
├── requirements.txt         # Dependências do projeto
├── Dockerfile             # Definição do container
├── docs/                 # Front-end (HTML, CSS, JS) publicado via GitHub Pages
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

## Como rodar localmente

```bash
# Clonar o repositório
git clone https://github.com/sugixp/task-api.git
cd task-api

# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Rodar o servidor
uvicorn main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`, com documentação interativa em `http://127.0.0.1:8000/docs`.

## Reativando o deploy na AWS

```bash
eb init          # se necessário reconfigurar localmente
eb create task-api-env
```

Após alguns minutos, o comando retorna a URL pública do ambiente ativo.

## Como rodar com Docker

```bash
docker build -t task-api .
docker run -p 8000:8000 task-api
```

## Rodando os testes

```bash
pytest -v
```

## Endpoints principais

| Método | Rota            | Descrição                          | Autenticação |
| ------ | --------------- | ---------------------------------- | ------------ |
| POST   | `/registrar`    | Cria um novo usuário               | Não          |
| POST   | `/login`        | Autentica e retorna token JWT      | Não          |
| GET    | `/tarefas`      | Lista as tarefas do usuário logado | Sim          |
| POST   | `/tarefas`      | Cria uma nova tarefa               | Sim          |
| GET    | `/tarefas/{id}` | Busca uma tarefa específica        | Sim          |
| PUT    | `/tarefas/{id}` | Atualiza uma tarefa                | Sim          |
| DELETE | `/tarefas/{id}` | Remove uma tarefa                  | Sim          |

## Front-end

Uma interface simples em HTML, CSS e JavaScript puro consome a API para demonstrar seu uso real: tela de login/registro e gerenciamento de tarefas (criar, marcar como concluída, remover). Está publicada via GitHub Pages, na pasta `docs/` deste mesmo repositório.

## Limitações conhecidas e próximos passos

Este projeto tem fins de estudo e portfólio, e algumas decisões refletem esse escopo:

- **Banco de dados SQLite dentro do container**: os dados não persistem entre reinicializações do ambiente na AWS. Em um cenário de produção, seria usado um banco gerenciado externo (ex: Amazon RDS).
- **CORS liberado para todas as origens (`*`)**: adequado para desenvolvimento e demonstração; em produção, seria restrito ao domínio específico do front-end.
- **API servida via HTTP (sem HTTPS)**: por essa razão, o front-end publicado via GitHub Pages (HTTPS) não consegue se conectar diretamente à API em produção — os navegadores bloqueiam esse tipo de requisição por segurança ("mixed content"). A solução correta seria colocar a API atrás de uma distribuição CloudFront (HTTPS gratuito), o que foi planejado e configurado parcialmente, mas não finalizado nesta versão devido a uma verificação de conta pendente do lado da AWS. O front-end funciona normalmente quando executado localmente, onde essa restrição de navegador não se aplica.
- **Próximos passos planejados**: finalizar a configuração de HTTPS via CloudFront, migrar para um banco de dados persistente, e adicionar paginação nas listagens.

## Autor

**Henrique Sadao Sugi**
Estudante de Análise e Desenvolvimento de Sistemas — PUCPR
[LinkedIn](https://www.linkedin.com/in/henrique-sugi-50b6152a5) · [GitHub](https://github.com/sugixp) · [Portfólio](https://sugixp.github.io/portfolio)
