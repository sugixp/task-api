from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt, JWTError

from database import Base, engine, SessionLocal
import models
import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    excecao_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY,
                             algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise excecao_credenciais
    except JWTError:
        raise excecao_credenciais

    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email).first()
    if usuario is None:
        raise excecao_credenciais
    return usuario


class TarefaSchema(BaseModel):
    titulo: str
    descricao: str
    concluida: bool = False


class UsuarioSchema(BaseModel):
    email: str
    senha: str


@app.get("/")
def raiz():
    return {"mensagem": "API no ar"}


@app.post("/registrar")
def registrar(dados: UsuarioSchema, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.email == dados.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo_usuario = models.Usuario(
        email=dados.email,
        senha_hash=auth.gerar_hash_senha(dados.senha)
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"mensagem": "Usuário criado com sucesso", "id": novo_usuario.id}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == form_data.username).first()
    if not usuario or not auth.verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=401, detail="Email ou senha incorretos")

    token = auth.criar_token_acesso({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/tarefas")
def criar_tarefa(tarefa: TarefaSchema, db: Session = Depends(get_db), usuario_atual: models.Usuario = Depends(get_usuario_atual)):
    nova_tarefa = models.Tarefa(
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        concluida=tarefa.concluida,
        dono_id=usuario_atual.id
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return nova_tarefa


@app.get("/tarefas")
def listar_tarefas(db: Session = Depends(get_db), usuario_atual: models.Usuario = Depends(get_usuario_atual)):
    return db.query(models.Tarefa).filter(models.Tarefa.dono_id == usuario_atual.id).all()


@app.get("/tarefas/{id_tarefa}")
def obter_tarefa(id_tarefa: int, db: Session = Depends(get_db), usuario_atual: models.Usuario = Depends(get_usuario_atual)):
    tarefa = db.query(models.Tarefa).filter(
        models.Tarefa.id == id_tarefa, models.Tarefa.dono_id == usuario_atual.id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tarefa


@app.put("/tarefas/{id_tarefa}")
def atualizar_tarefa(id_tarefa: int, dados: TarefaSchema, db: Session = Depends(get_db), usuario_atual: models.Usuario = Depends(get_usuario_atual)):
    tarefa = db.query(models.Tarefa).filter(
        models.Tarefa.id == id_tarefa, models.Tarefa.dono_id == usuario_atual.id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    tarefa.titulo = dados.titulo
    tarefa.descricao = dados.descricao
    tarefa.concluida = dados.concluida

    db.commit()
    db.refresh(tarefa)
    return tarefa


@app.delete("/tarefas/{id_tarefa}")
def deletar_tarefa(id_tarefa: int, db: Session = Depends(get_db), usuario_atual: models.Usuario = Depends(get_usuario_atual)):
    tarefa = db.query(models.Tarefa).filter(
        models.Tarefa.id == id_tarefa, models.Tarefa.dono_id == usuario_atual.id).first()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    db.delete(tarefa)
    db.commit()
    return {"mensagem": "Tarefa removida com sucesso"}
