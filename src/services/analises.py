from typing import Dict, List
from sqlmodel import Session, func, select
from ..models import Favorecido, Municipio, Transferencia


def total_transferencias_por_estado(session: Session, limit: int = 100) -> List[Dict]:
    result = session.exec(
        select(
            Municipio.uf,
            func.count(Transferencia.id).label("total_transferencias"),
            func.sum(Transferencia.valor).label("valor_total"),
        )
        .join(Favorecido, Favorecido.municipio_codigo == Municipio.codigo)
        .join(Transferencia, Transferencia.favorecido_codigo == Favorecido.codigo)
        .group_by(Municipio.uf)
        .order_by(func.count(Transferencia.id).desc())
        .limit(limit)
    ).all()

    return [
        {
            "uf": uf,
            "total_transferencias": total_transferencias or 0,
            "valor_total": valor_total or 0,
        }
        for uf, total_transferencias, valor_total in result
    ]
