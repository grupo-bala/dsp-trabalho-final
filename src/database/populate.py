import pandas as pd
from decimal import Decimal
from .infra import get_session
from ..models import (
    Municipio,
    UnidadeGestora,
    Favorecido,
    Programa,
    Transferencia,
    ProgramaTransferencia,
)


def populate_data():
    df_municipios = pd.read_csv("municipios_clean.csv")
    municipios = []
    for _, row in df_municipios.iterrows():
        municipio = Municipio(
            codigo=row["codigo_municipio_siafi"],
            nome=row["nome_municipio"],
            uf=row["uf"],
        )
        municipios.append(municipio)
    get_session().add_all(municipios)
    get_session().commit()

    df_unidades = pd.read_csv("unidades_gestoras_clean.csv")
    unidades = []
    for _, row in df_unidades.iterrows():
        unidade = UnidadeGestora(
            codigo=row["codigo_unidade_gestora"],
            nome=row["nome_unidade_gestora"],
            orgao_nome=row["nome_orgao"],
        )
        unidades.append(unidade)
    get_session().add_all(unidades)
    get_session().commit()

    df_favorecidos = pd.read_csv("favorecidos_clean.csv")
    favorecidos = []
    for _, row in df_favorecidos.iterrows():
        favorecido = Favorecido(
            codigo=row["codigo_favorecido"],
            nome=row["nome_favorecido"],
            municipio_codigo=row["codigo_municipio_siafi"],
        )
        favorecidos.append(favorecido)
    get_session().add_all(favorecidos)
    get_session().commit()

    df_programas = pd.read_csv("programas_clean.csv")
    programas = []
    for _, row in df_programas.iterrows():
        programa = Programa(codigo=row["codigo_programa"], nome=row["nome_programa"])
        programas.append(programa)
    get_session().add_all(programas)
    get_session().commit()

    df_transferencias = pd.read_csv("transferencias_clean.csv")
    transferencias = []
    for _, row in df_transferencias.iterrows():
        valor = row["valor"]
        if isinstance(valor, str):
            try:
                valor = Decimal(valor)
            except Exception:
                valor = None
        transferencia = Transferencia(
            id=row["id"],
            tipo=row["tipo"],
            valor=valor,
            unidade_gestora_codigo=row["unidade_gestora_codigo"],
            favorecido_codigo=row["favorecido_codigo"],
        )
        transferencias.append(transferencia)
    get_session().add_all(transferencias)
    get_session().commit()

    df_pt = pd.read_csv("programa_transferencia_clean.csv")
    pt_links = []
    for _, row in df_pt.iterrows():
        link = ProgramaTransferencia(
            transferencia_id=row["transferencia_id"],
            programa_codigo=row["programa_codigo"],
        )
        pt_links.append(link)
    get_session().add_all(pt_links)
    get_session().commit()
