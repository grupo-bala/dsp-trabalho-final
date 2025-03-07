from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, func
from src.models import Favorecido
from src.database.infra import get_session

router = APIRouter(prefix="/favorecidos", tags=["Favorecidos"])


@router.post("/", response_model=Favorecido)
def create_favorecido(favorecido: Favorecido, session: Session = Depends(get_session)):
    try:
        session.add(favorecido)
        session.commit()
        session.refresh(favorecido)

        return favorecido
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar favorecido: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
def read_favorecidos(
    session: Session = Depends(get_session),
    skip: int = Query(0, alias="offset", ge=0),
    limit: int = Query(10, le=100),
    codigo: Optional[int] = Query(None),
    nome: Optional[str] = Query(None),
    municipio: Optional[int] = Query(None),
) -> Dict[str, Any]:
    try:
        query = select(Favorecido)

        if codigo is not None:
            query = query.where(Favorecido.codigo == codigo)
        if nome is not None:
            query = query.where(Favorecido.nome.contains(nome))  # Corrigido o filtro de nome
        if municipio is not None:
            query = query.where(Favorecido.municipio.codigo == municipio)

        total = session.exec(select(func.count()).select_from(Favorecido)).one()

        favorecidos = session.exec(query.offset(skip).limit(limit)).all()

        return {
            "data": favorecidos,
            "total": total,
            "offset": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar favorecidos: {str(e)}"
        )



@router.get("/{codigo}", response_model=Favorecido)
def read_favorecido(codigo: int, session: Session = Depends(get_session)):
    favorecido = session.get(Favorecido, codigo)

    if not favorecido:
        raise HTTPException(status_code=404, detail="Favorecido não encontrado")

    return favorecido


@router.put("/{codigo}", response_model=Favorecido)
def update_favorecido(
    codigo: int, favorecido_update: Favorecido, session: Session = Depends(get_session)
):
    favorecido = session.get(Favorecido, codigo)

    if not favorecido:
        raise HTTPException(status_code=404, detail="Favorecido não encontrado")

    try:
        update_data = favorecido_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(Favorecido, key, value)

        session.add(favorecido)
        session.commit()
        session.refresh(favorecido)

        return favorecido
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar favorecido: {str(e)}"
        )


@router.delete("/{codigo}", response_model=Favorecido)
def delete_favorecido(codigo: int, session: Session = Depends(get_session)):
    favorecido = session.get(Favorecido, codigo)

    if not favorecido:
        raise HTTPException(status_code=404, detail="Favorecido não encontrado")

    try:
        session.delete(favorecido)
        session.commit()

        return favorecido
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao deletar favorecido: {str(e)}"
        )
