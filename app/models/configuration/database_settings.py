"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : database_settings.py
Descrição : Representa as configurações de acesso ao banco de dados.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class DatabaseSettings(
    BaseModel,
):
    """
    Representa as configurações de conexão com o banco de dados.
    """

    server: str = ""

    port: int = 1433

    database: str = ""

    username: str | None = None

    password: str | None = None

    driver: str = (
        "ODBC Driver 18 for SQL Server"
    )

    trusted_connection: bool = False

    encrypt: bool = True

    trust_server_certificate: bool = True

    connection_timeout: int = 30