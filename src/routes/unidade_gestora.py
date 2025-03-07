from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from src.models import UnidadeGestora
from src.database.infra import get_session

router = APIRouter(prefix="/unidades_gestoras", tags=["Unidades Gestora"])


@router.post("/", response_model=UnidadeGestora)
def create_unidade_gestora(
    unidade_gestora: UnidadeGestora, session: Session = Depends(get_session)
):
    try:
        session.add(unidade_gestora)
        session.commit()
        session.refresh(unidade_gestora)
        return unidade_gestora
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar unidade gestora: {str(e)}"
        )


@router.get("/", response_model=List[UnidadeGestora])
def read_unidades_gestoras(
    session: Session = Depends(get_session),
    skip: int = Query(0, alias="offset", ge=0),
    limit: int = Query(10, le=100),
    orgao_nome: Optional[str] = Query(None, alias="orgao_nome"),
):
    try:
        query = select(UnidadeGestora)
        if orgao_nome:
            query = query.where(UnidadeGestora.orgao_nome.contains(orgao_nome))
        unidades_gestoras = session.exec(query.offset(skip).limit(limit)).all()
        return unidades_gestoras
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar unidade gestora: {str(e)}"
        )


@router.get("/{codigo}", response_model=UnidadeGestora)
def read_unidade_gestora(codigo: int, session: Session = Depends(get_session)):
    unidade_gestora = session.get(UnidadeGestora, codigo)
    if not unidade_gestora:
        raise HTTPException(status_code=404, detail="Unidade gestora não encontrado")
    return unidade_gestora


@router.put("/{codigo}", response_model=UnidadeGestora)
def update_unidade_gestora(
    codigo: int,
    unidade_gestora_update: UnidadeGestora,
    session: Session = Depends(get_session),
):
    unidade_gestora = session.get(UnidadeGestora, codigo)
    if not unidade_gestora:
        raise HTTPException(status_code=404, detail="Unidade gestora não encontrada")
    try:
        update_data = unidade_gestora_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(unidade_gestora, key, value)
        session.add(unidade_gestora)
        session.commit()
        session.refresh(unidade_gestora)
        return unidade_gestora
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar unidade gestora: {str(e)}"
        )


@router.delete("/{codigo}", response_model=UnidadeGestora)
def delete_unidade_gestora(codigo: int, session: Session = Depends(get_session)):
    unidade_gestora = session.get(UnidadeGestora, codigo)
    if not unidade_gestora:
        raise HTTPException(status_code=404, detail="Unidade gestora não encontrada")
    try:
        session.delete(unidade_gestora)
        session.commit()
        return unidade_gestora
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao deletar unidade gestora: {str(e)}"
        )
