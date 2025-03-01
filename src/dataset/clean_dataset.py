import re
import unicodedata
from decimal import Decimal

import chardet
import pandas as pd


def to_snake_case(s):
    s = s.strip().lower()
    s = "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s


file_path = "raw_dataset_transferencias.csv"

with open(file_path, "rb") as f:
    result = chardet.detect(f.read(100000))
encoding = result["encoding"]

df = pd.read_csv(file_path, encoding=encoding, delimiter=";", dtype=str)

df.columns = [to_snake_case(col) for col in df.columns]

if "ano__mês" in df.columns:
    df.drop(columns=["ano__mês"], inplace=True)

df.dropna(inplace=True)

columns_to_clean = [
    "nome_unidade_gestora",
    "nome_favorecido",
    "nome_programa",
    "tipo_transferencia",
]
for col in columns_to_clean:
    if col in df.columns:
        df[col] = df[col].replace('"', "", regex=False)


def to_decimal(val):
    if pd.isna(val):
        return None
    val = val.replace(".", "").replace(",", ".")
    try:
        return Decimal(val)
    except RuntimeError:
        return None


if "valor_transferido" in df.columns:
    df["valor_transferido"] = df["valor_transferido"].apply(to_decimal)

numeric_cols = ["codigo_municipio_siafi", "codigo_unidade_gestora", "codigo_programa"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df_municipios = df[["codigo_municipio_siafi", "nome_municipio", "uf"]].drop_duplicates()
df_unidades = df[
    ["codigo_unidade_gestora", "nome_unidade_gestora", "nome_orgao"]
].drop_duplicates()
df_favorecidos = df[
    ["codigo_favorecido", "nome_favorecido", "codigo_municipio_siafi"]
].drop_duplicates()
df_programas = df[["codigo_programa", "nome_programa"]].drop_duplicates()

df_transferencias = df.copy()
df_transferencias.reset_index(drop=True, inplace=True)
df_transferencias["id"] = df_transferencias.index + 1

df_transferencias = df_transferencias[
    [
        "id",
        "tipo_transferencia",
        "valor_transferido",
        "codigo_unidade_gestora",
        "codigo_favorecido",
        "codigo_programa",
    ]
]

df_transferencias.rename(
    columns={
        "tipo_transferencia": "tipo",
        "valor_transferido": "valor",
        "codigo_unidade_gestora": "unidade_gestora_codigo",
        "codigo_favorecido": "favorecido_codigo",
        "codigo_programa": "programa_codigo",
    },
    inplace=True,
)

df_programa_transferencia = df_transferencias[["id", "programa_codigo"]].copy()
df_programa_transferencia.rename(columns={"id": "transferencia_id"}, inplace=True)

df_municipios.to_csv("municipios_clean.csv", index=False, encoding="utf-8")
df_unidades.to_csv("unidades_gestoras_clean.csv", index=False, encoding="utf-8")
df_favorecidos.to_csv("favorecidos_clean.csv", index=False, encoding="utf-8")
df_programas.to_csv("programas_clean.csv", index=False, encoding="utf-8")
df_transferencias.to_csv("transferencias_clean.csv", index=False, encoding="utf-8")
df_programa_transferencia.to_csv(
    "programa_transferencia_clean.csv", index=False, encoding="utf-8"
)

print("Dataset tratado, limpo e preparado com sucesso!")
