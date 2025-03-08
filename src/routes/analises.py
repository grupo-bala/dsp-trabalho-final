import io
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlmodel import Session, select, func
from typing import List, Dict
from src.database.infra import get_session
from src.models import Favorecido, UnidadeGestora, Transferencia, Programa
from ..services.analises import total_transferencias_por_estado

router = APIRouter(prefix="/analises", tags=["Análises"])
matplotlib.use("Agg")


@router.get("/total-transferencias-por-estado")
def get_total_transferencias_por_estado(
    session: Session = Depends(get_session),
) -> List[Dict]:
    try:
        return total_transferencias_por_estado(session)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular total de transferências por município: {str(e)}",
        )


@router.get("/grafico-transferencias-por-estado")
def grafico_transferencias_por_estado(session: Session = Depends(get_session)):
    dados = total_transferencias_por_estado(session, 10)

    estados = [d["uf"] for d in dados]
    totais = [d["total_transferencias"] for d in dados]
    colors = sns.color_palette("Set3", 10)
    colors = [color for color in colors]

    plt.figure(figsize=(10, 8))
    plt.pie(
        totais,
        labels=estados,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops={"edgecolor": "black"},
    )

    plt.title(
        "Distribuição de Transferências pelos 10 Estado Mais Representativos",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    plt.axis("equal")

    img_io = io.BytesIO()
    plt.savefig(img_io, format="png", bbox_inches="tight", dpi=100)
    plt.close()

    img_io.seek(0)
    return Response(img_io.getvalue(), media_type="image/png")


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
