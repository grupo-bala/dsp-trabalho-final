from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, func
from src.models import Programa, ProgramaTransferencia
from src.database.infra import get_session

router = APIRouter(prefix="/programas", tags=["Programas"])


@router.post("/", response_model=Programa)
def create_programa(programa: Programa, session: Session = Depends(get_session)):
    try:
        session.add(programa)
        session.commit()
        session.refresh(programa)
        return programa
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar programa: {str(e)}")


@router.get("/", response_model=Dict[str, Any])
def read_programas(
    session: Session = Depends(get_session),
    skip: int = Query(0, alias="offset", ge=0),
    limit: int = Query(10, alias="limit", le=100),
    nome: Optional[str] = Query(None, alias="nome"),
) -> Dict[str, Any]:
    try:
        query = select(Programa)
        if nome:
            query = query.where(Programa.nome.contains(nome))

        total = session.exec(select(func.count()).select_from(Programa)).one()
        programas = session.exec(query.offset(skip).limit(limit)).all()

        return {"data": programas, "total": total, "offset": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar programas: {str(e)}"
        )


@router.get("/{codigo}", response_model=Programa)
def read_programa(codigo: int, session: Session = Depends(get_session)):
    programa = session.get(Programa, codigo)
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    return programa


@router.put("/{codigo}", response_model=Programa)
def update_programa(
    codigo: int, programa_update: Programa, session: Session = Depends(get_session)
):
    programa = session.get(Programa, codigo)
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    try:
        update_data = programa_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(programa, key, value)
        session.add(programa)
        session.commit()
        session.refresh(programa)
        return programa
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar programa: {str(e)}"
        )


@router.delete("/{codigo}", response_model=Programa)
def delete_programa(codigo: int, session: Session = Depends(get_session)):
    programa = session.get(Programa, codigo)
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    try:
        session.delete(programa)
        session.commit()
        return programa
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao deletar programa: {str(e)}"
        )
