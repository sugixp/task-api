from datetime import datetime, timedelta, UTC
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "troque-isso-por-uma-chave-secreta-de-verdade"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha_texto: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_texto, senha_hash)


def criar_token_acesso(dados: dict) -> str:
    dados_para_codificar = dados.copy()
    expira_em = datetime.now(
        UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_para_codificar.update({"exp": expira_em})
    return jwt.encode(dados_para_codificar, SECRET_KEY, algorithm=ALGORITHM)
