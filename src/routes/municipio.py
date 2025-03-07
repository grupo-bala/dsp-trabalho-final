from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from src.models import Municipio, Favorecido
from src.database.infra import get_session

router = APIRouter()


@router.post("/municipios/", response_model=Municipio)
def create_municipio(municipio: Municipio, session: Session = Depends(get_session)):
    try:
        session.add(municipio)
        session.commit()
        session.refresh(municipio)
        return municipio
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar município: {str(e)}"
        )


@router.get("/municipios/")
def read_municipios(
    session: Session = Depends(get_session),
    skip: int = Query(0, alias="offset", ge=0),
    limit: int = Query(10, alias="limit", le=100),
    nome: Optional[str] = Query(None, alias="nome"),
    uf: Optional[str] = Query(None, alias="uf"),
    codigo: Optional[int] = Query(None, alias="codigo"),
) -> Dict[str, Any]:
    try:
        query = select(Municipio)
        if nome:
            query = query.where(Municipio.nome.contains(nome))
        if uf:
            query = query.where(Municipio.uf == uf)
        if codigo:
            query = query.where(Municipio.codigo == codigo)
        total = session.exec(select(Municipio).count()).one()
        municipios = session.exec(query.offset(skip).limit(limit)).all()
        return {"total": total, "offset": skip, "limit": limit, "data": municipios}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar municípios: {str(e)}"
        )


@router.get("/municipios/{codigo}", response_model=Municipio)
def read_municipio(codigo: int, session: Session = Depends(get_session)):
    municipio = session.get(Municipio, codigo)
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return municipio


@router.put("/municipios/{codigo}", response_model=Municipio)
def update_municipio(
    codigo: int, municipio_update: Municipio, session: Session = Depends(get_session)
):
    municipio = session.get(Municipio, codigo)
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    try:
        update_data = municipio_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(municipio, key, value)
        session.add(municipio)
        session.commit()
        session.refresh(municipio)
        return municipio
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar município: {str(e)}"
        )


@router.delete("/municipios/{codigo}", response_model=Municipio)
def delete_municipio(codigo: int, session: Session = Depends(get_session)):
    municipio = session.get(Municipio, codigo)
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    try:
        session.delete(municipio)
        session.commit()
        return municipio
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao deletar município: {str(e)}"
        )


@router.get("/municipios/favorecidos/count")
def count_favorecidos_por_municipio(session: Session = Depends(get_session)):
    try:
        municipios_com_favorecidos = session.exec(
            select(
                Municipio.codigo,
                Municipio.nome,
                Municipio.uf,
                (
                    select(Favorecido)
                    .where(Favorecido.municipio_codigo == Municipio.codigo)
                    .count()
                ),
            )
        ).all()
        return {
            "data": [
                {
                    "codigo_municipio": codigo,
                    "nome": nome,
                    "uf": uf,
                    "numero_de_favorecidos": count,
                }
                for codigo, nome, uf, count in municipios_com_favorecidos
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar número de favorecidos por município: {str(e)}",
        )
