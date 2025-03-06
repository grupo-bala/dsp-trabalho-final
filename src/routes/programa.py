from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from src.models import Programa
from src.database.infra import get_session

router = APIRouter(prefix="/programas", tags=["Programas"])

@router.post("/programas/", response_model=Programa)
def create_programa(programa: Programa, session: Session = Depends(get_session)):
    try:
        session.add(programa)
        session.commit()
        session.refresh(programa)
        return programa
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar programa: {str(e)}")

@router.get("/programas/", response_model=List[Programa])
def read_programas(
    session: Session = Depends(get_session),
    skip: int = Query(0, alias="offset", ge=0),
    limit: int = Query(10, le=100),
    nome: Optional[str] = Query(None, alias="nome")
):
    try:
        query = select(Programa)
        if nome:
            query = query.where(Programa.nome.contains(nome))  # Filtra pelo nome do programa
        programas = session.exec(query.offset(skip).limit(limit)).all()
        return programas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar programas: {str(e)}")

@router.get("/programas/{codigo}", response_model=Programa)
def read_programa(codigo: int, session: Session = Depends(get_session)):
    programa = session.get(Programa, codigo)
    if not programa:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    return programa

@router.put("/programas/{codigo}", response_model=Programa)
def update_programa(codigo: int, programa_update: Programa, session: Session = Depends(get_session)):
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
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar programa: {str(e)}")

@router.delete("/programas/{codigo}", response_model=Programa)
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
        raise HTTPException(status_code=500, detail=f"Erro ao deletar programa: {str(e)}")
