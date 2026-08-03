from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)

    tarefas = relationship("Tarefa", back_populates="dono")


class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descricao = Column(String)
    concluida = Column(Boolean, default=False)
    dono_id = Column(Integer, ForeignKey("usuarios.id"))

    dono = relationship("Usuario", back_populates="tarefas")
