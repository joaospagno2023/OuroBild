"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_database_connection.py
Descrição : Testa a conexão com o banco de dados.
--------------------------------------------------------------------
"""

from unittest.mock import (
    MagicMock,
)

from app.database.connection import (
    DatabaseConnection,
)

from app.models.configuration.database_settings import (
    DatabaseSettings,
)


def test_deve_criar_database_connection():
    """
    Deve criar a infraestrutura de conexão.
    """

    settings = DatabaseSettings(
        server="servidor-teste",
        port=1433,
        database="ourobuild",
        username="usuario",
        password="senha",
    )

    connection = DatabaseConnection(
        settings=settings,
    )

    assert connection is not None
    assert connection.engine is not None


def test_deve_rejeitar_settings_nulo():
    """
    Deve rejeitar configuração inexistente.
    """

    try:
        DatabaseConnection(
            settings=None,
        )

        assert False

    except ValueError as exception:

        assert str(exception) == (
            "DatabaseSettings não foi informado."
        )