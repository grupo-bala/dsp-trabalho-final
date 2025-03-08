from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, func
from src.models import Transferencia, UnidadeGestora
from src.database.infra import get_session

router = APIRouter(prefix="/transferencias", tags=["Transferências"])


@router.post("/", response_model=Transferencia)
def create_transferencia(
    transferencia: Transferencia, session: Session = Depends(get_session)
):
    try:
        session.add(transferencia)
        session.commit()
        session.refresh(transferencia)
        return transferencia
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar transferencia: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
def read_transferencia(
    session: Session = Depends(get_session),
    skip: int = Query(0, alias="offset", ge=0),
    limit: int = Query(10, le=100),
    tipo: Optional[str] = Query(None, alias="tipo"),
) -> Dict[str, Any]:
    try:
        query = select(Transferencia)
        if tipo:
            query = query.where(Transferencia.tipo.contains(tipo))

        total = session.exec(select(func.count()).select_from(Transferencia)).one()

        transferencia = session.exec(query.offset(skip).limit(limit)).all()

        return {"data": transferencia, "total": total, "offset": skip, "limit": limit}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar transferências: {str(e)}"
        )


@router.get("/{unidade_gestora}/statistics", response_model=Dict[str, Any])
def read_transferencia_estatisticas(
    unidade_gestora: int, session: Session = Depends(get_session)
) -> Dict[str, Any]:
    try:
        resultado = session.exec(
            select(
                UnidadeGestora.nome,
                UnidadeGestora.orgao_nome,
                func.max(Transferencia.valor),
                func.min(Transferencia.valor),
                func.sum(Transferencia.valor),
                func.round(func.avg(Transferencia.valor), 2),
                func.count(Transferencia.id),
            )
            .join(
                UnidadeGestora,
                UnidadeGestora.codigo == Transferencia.unidade_gestora_codigo,
            )
            .where(Transferencia.unidade_gestora_codigo == unidade_gestora)
            .group_by(UnidadeGestora.nome, UnidadeGestora.orgao_nome)
        ).one_or_none()

        if not resultado:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma transferência encontrada para essa unidade gestora",
            )

        return {
            "unidade_gestora": resultado[0],
            "orgao": resultado[1],
            "transferencia_maxima": resultado[2],
            "transferencia_minima": resultado[3],
            "transferencia_valor_total": resultado[4],
            "transferencia_valor_medio": resultado[5],
            "quantidade_transferencias": resultado[6],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}"
        )


@router.get("/{codigo}", response_model=Transferencia)
def read_transferencia(codigo: int, session: Session = Depends(get_session)):
    transferencia = session.get(Transferencia, codigo)
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferencia não encontrado")
    return transferencia


@router.put("/{codigo}", response_model=Transferencia)
def update_transferencia(
    codigo: int,
    transferencia_update: Transferencia,
    session: Session = Depends(get_session),
):
    transferencia = session.get(Transferencia, codigo)
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferencia não encontrada")
    try:
        update_data = transferencia_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(transferencia, key, value)
        session.add(transferencia)
        session.commit()
        session.refresh(transferencia)
        return transferencia
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar transferencia: {str(e)}"
        )


@router.delete("/{codigo}", response_model=Transferencia)
def delete_transferencia(codigo: int, session: Session = Depends(get_session)):
    transferencia = session.get(Transferencia, codigo)
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferencia não encontrada")
    try:
        session.delete(transferencia)
        session.commit()
        return transferencia
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao deletar transferencia: {str(e)}"
        )
