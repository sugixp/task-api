import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def preparar_banco():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_registrar_usuario():
    resposta = client.post("/registrar", json={
        "email": "usuario@teste.com",
        "senha": "senha123"
    })
    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == "Usuário criado com sucesso"


def test_nao_permite_email_duplicado():
    client.post(
        "/registrar", json={"email": "duplicado@teste.com", "senha": "senha123"})
    resposta = client.post(
        "/registrar", json={"email": "duplicado@teste.com", "senha": "outrasenha"})
    assert resposta.status_code == 400


def test_login_com_sucesso():
    client.post(
        "/registrar", json={"email": "login@teste.com", "senha": "senha123"})
    resposta = client.post(
        "/login", data={"username": "login@teste.com", "password": "senha123"})
    assert resposta.status_code == 200
    assert "access_token" in resposta.json()


def test_login_com_senha_errada():
    client.post(
        "/registrar", json={"email": "erro@teste.com", "senha": "senha123"})
    resposta = client.post(
        "/login", data={"username": "erro@teste.com", "password": "senhaerrada"})
    assert resposta.status_code == 401


def test_criar_tarefa_sem_autenticacao():
    resposta = client.post("/tarefas", json={
        "titulo": "Tarefa sem login",
        "descricao": "Não deveria funcionar",
        "concluida": False
    })
    assert resposta.status_code == 401


def test_criar_e_listar_tarefa_autenticado():
    client.post(
        "/registrar", json={"email": "tarefa@teste.com", "senha": "senha123"})
    resposta_login = client.post(
        "/login", data={"username": "tarefa@teste.com", "password": "senha123"})
    token = resposta_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    resposta_criar = client.post("/tarefas", json={
        "titulo": "Tarefa autenticada",
        "descricao": "Deve funcionar",
        "concluida": False
    }, headers=headers)
    assert resposta_criar.status_code == 200
    assert resposta_criar.json()["titulo"] == "Tarefa autenticada"

    resposta_listar = client.get("/tarefas", headers=headers)
    assert resposta_listar.status_code == 200
    assert len(resposta_listar.json()) == 1
