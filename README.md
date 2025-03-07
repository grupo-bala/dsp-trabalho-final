# Dataset Utilizado

As entidades foram criadas apartir de um dataset dos [Recursos Transferidos](https://portaldatransparencia.gov.br/download-de-dados/transferencias).

| Entidades         | 
| :---------------- |
| Município         |
| Órgão             |
| Unidade Gestora   |
| Favorecido        |
| Função            |
| Programa          |
| Transferência     |

# Forma de uso

Instale o python uv
```
pip install uv
```

Rodar o Projeto
```
uv run fastapi dev src/main.py
```

Para popular o banco de dados
```
python -m src.database.populate  
```