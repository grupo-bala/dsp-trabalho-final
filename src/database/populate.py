import os
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

current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, "../dataset/")


def populate_data():
    session = next(get_session())

    try:
        df_municipios = pd.read_csv(os.path.join(dataset_path, "municipios_clean.csv"))
        municipios = []
        for _, row in df_municipios.iterrows():
            municipio = Municipio(
                codigo=row["codigo_municipio_siafi"],
                nome=row["nome_municipio"],
                uf=row["uf"],
            )
            municipios.append(municipio)
        session.add_all(municipios)
        session.commit()

        df_unidades = pd.read_csv(
            os.path.join(dataset_path, "unidades_gestoras_clean.csv")
        )
        unidades = []
        for _, row in df_unidades.iterrows():
            unidade = UnidadeGestora(
                codigo=row["codigo_unidade_gestora"],
                nome=row["nome_unidade_gestora"],
                orgao_nome=row["nome_orgao"],
            )
            unidades.append(unidade)
        session.add_all(unidades)
        session.commit()

        df_favorecidos = pd.read_csv(
            os.path.join(dataset_path, "favorecidos_clean.csv")
        )
        favorecidos = []
        for _, row in df_favorecidos.iterrows():
            favorecido = Favorecido(
                codigo=row["codigo_favorecido"],
                nome=row["nome_favorecido"],
                municipio_codigo=row["codigo_municipio_siafi"],
            )
            favorecidos.append(favorecido)
        session.add_all(favorecidos)
        session.commit()

        df_programas = pd.read_csv(os.path.join(dataset_path, "programas_clean.csv"))
        programas = []
        for _, row in df_programas.iterrows():
            programa = Programa(
                codigo=row["codigo_programa"], nome=row["nome_programa"]
            )
            programas.append(programa)
        session.add_all(programas)
        session.commit()

        df_transferencias = pd.read_csv(
            os.path.join(dataset_path, "transferencias_clean.csv")
        )
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
        session.add_all(transferencias)
        session.commit()

        df_pt = pd.read_csv(
            os.path.join(dataset_path, "programa_transferencia_clean.csv")
        )
        pt_links = []
        for _, row in df_pt.iterrows():
            link = ProgramaTransferencia(
                transferencia_id=int(row["transferencia_id"]),
                programa_codigo=int(row["programa_codigo"]),
            )
            pt_links.append(link)
        session.add_all(pt_links)
        session.commit()
    except Exception as error:
        session.rollback()
        print(f"Erro: {str(error)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Populando o banco de dados...")
    populate_data()
    print("População concluída com sucesso!")
