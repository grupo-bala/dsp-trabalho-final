from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, func
from typing import List, Dict
from src.database.infra import get_session
from src.models import Municipio, UnidadeGestora, Transferencia, Programa, Favorecido

router = APIRouter(prefix="/analises", tags=["Análises"])


@router.get("/total-transferencias-por-municipio")
def get_total_transferencias_por_municipio(
    session: Session = Depends(get_session),
) -> List[Dict]:
    try:
        result = session.exec(
            select(
                Municipio.codigo,
                Municipio.nome,
                Municipio.uf,
                (
                    select(func.count())
                    .where(Transferencia.favorecido_codigo == Favorecido.codigo)
                    .where(Favorecido.municipio_codigo == Municipio.codigo)
                )
                .scalar_subquery()
                .label("total_transferencias"),
                (
                    select(func.sum(Transferencia.valor))
                    .where(Transferencia.favorecido_codigo == Favorecido.codigo)
                    .where(Favorecido.municipio_codigo == Municipio.codigo)
                )
                .scalar_subquery()
                .label("valor_total"),
            )
        ).all()

        return [
            {
                "codigo_municipio": codigo,
                "nome": nome,
                "uf": uf,
                "total_transferencias": total_transferencias or 0,
                "valor_total": valor_total or 0,
            }
            for codigo, nome, uf, total_transferencias, valor_total in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular total de transferências por município: {str(e)}",
        )


@router.get("/favorecidos-por-programa")
def get_favorecidos_por_programa(session: Session = Depends(get_session)) -> List[Dict]:
    try:
        result = session.exec(
            select(
                Programa.codigo,
                Programa.nome,
                (
                    select(func.count(Favorecido.codigo)).where(
                        Favorecido.codigo == Transferencia.favorecido_codigo
                    )
                )
                .scalar_subquery()
                .label("total_favorecidos"),
            )
        ).all()

        return [
            {
                "codigo_programa": codigo,
                "nome": nome,
                "total_favorecidos": total_favorecidos or 0,
            }
            for codigo, nome, total_favorecidos in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular favorecidos por programa: {str(e)}",
        )


@router.get("/total-transferencias-por-unidade-gestora")
def get_total_transferencias_por_unidade_gestora(
    session: Session = Depends(get_session),
) -> List[Dict]:
    try:
        result = session.exec(
            select(
                UnidadeGestora.codigo,
                UnidadeGestora.nome,
                UnidadeGestora.orgao_nome,
                (
                    select(func.count()).where(
                        Transferencia.unidade_gestora_codigo == UnidadeGestora.codigo
                    )
                )
                .scalar_subquery()
                .label("total_transferencias"),
                (
                    select(func.sum(Transferencia.valor)).where(
                        Transferencia.unidade_gestora_codigo == UnidadeGestora.codigo
                    )
                )
                .scalar_subquery()
                .label("valor_total"),
            )
        ).all()

        return [
            {
                "codigo_unidade_gestora": codigo,
                "nome": nome,
                "orgao_nome": orgao_nome,
                "total_transferencias": total_transferencias or 0,
                "valor_total": valor_total or 0,
            }
            for codigo, nome, orgao_nome, total_transferencias, valor_total in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular total de transferências por unidade gestora: {str(e)}",
        )


@router.get("/programas-mais-frequentes")
def get_programas_mais_frequentes(
    session: Session = Depends(get_session),
) -> List[Dict]:
    try:
        result = session.exec(
            select(
                Programa.codigo,
                Programa.nome,
                (
                    select(func.count()).where(
                        Transferencia.programas.any(Programa.codigo == Programa.codigo)
                    )
                )
                .scalar_subquery()
                .label("total_transferencias"),
            )
        ).all()

        return [
            {
                "codigo_programa": codigo,
                "nome": nome,
                "total_transferencias": total_transferencias or 0,
            }
            for codigo, nome, total_transferencias in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular programas mais frequentes: {str(e)}",
        )
