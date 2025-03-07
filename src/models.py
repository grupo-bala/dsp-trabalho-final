from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from decimal import Decimal


class Municipio(SQLModel, table=True):
    codigo: int = Field(primary_key=True)
    nome: str
    uf: str
    favorecidos: List["Favorecido"] = Relationship(
        back_populates="municipio",
        sa_relationship_kwargs={"cascade": "all, delete, delete-orphan"}
    )


class UnidadeGestora(SQLModel, table=True):
    codigo: int = Field(primary_key=True)
    nome: str
    orgao_nome: str
    transferencias: List["Transferencia"] = Relationship(
        back_populates="unidade_gestora",
        sa_relationship_kwargs={"cascade": "all, delete, delete-orphan"}
    )


class Favorecido(SQLModel, table=True):
    codigo: str = Field(primary_key=True)
    nome: str
    municipio_codigo: int = Field(
        foreign_key="municipio.codigo",
        sa_column_kwargs={'ondelete': 'CASCADE'}
    )
    municipio: Municipio = Relationship(back_populates="favorecidos")
    transferencias: List["Transferencia"] = Relationship(
        back_populates="favorecido",
        sa_relationship_kwargs={"cascade": "all, delete, delete-orphan"}
    )


class ProgramaTransferencia(SQLModel, table=True):
    transferencia_id: int = Field(
        foreign_key="transferencia.id", 
        primary_key=True,
        sa_column_kwargs={'ondelete': 'CASCADE'}
    )
    programa_codigo: int = Field(
        foreign_key="programa.codigo",
        primary_key=True,
        sa_column_kwargs={'ondelete': 'CASCADE'}
    )


class Programa(SQLModel, table=True):
    codigo: int = Field(primary_key=True)
    nome: str
    transferencias: List["Transferencia"] = Relationship(
        back_populates="programas", 
        link_model=ProgramaTransferencia,
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


class Transferencia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str
    valor: Decimal
    unidade_gestora_codigo: int = Field(
        foreign_key="unidadegestora.codigo",
        sa_column_kwargs={'ondelete': 'CASCADE'}
    )
    favorecido_codigo: str = Field(
        foreign_key="favorecido.codigo",
        sa_column_kwargs={'ondelete': 'CASCADE'}
    )
    unidade_gestora: UnidadeGestora = Relationship(back_populates="transferencias")
    favorecido: Favorecido = Relationship(back_populates="transferencias")
    programas: List[Programa] = Relationship(
        back_populates="transferencias",
        link_model=ProgramaTransferencia,
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
