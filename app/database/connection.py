"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : connection.py
Descrição : Gerencia a conexão com o banco de dados SQL Server.
--------------------------------------------------------------------
"""

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.engine import (
    URL,
)
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

from app.models.configuration.database_settings import (
    DatabaseSettings,
)


class DatabaseConnection:
    """
    Cria e disponibiliza a conexão com o banco SQL Server.
    """

    def __init__(
        self,
        settings: DatabaseSettings,
    ) -> None:
        """
        Inicializa a conexão com o banco.

        Args:
            settings: Configurações do banco de dados.
        """

        if settings is None:
            raise ValueError(
                "DatabaseSettings não foi informado."
            )

        self.__settings = settings

        self.__engine = self.__create_engine()

        self.__session_factory = sessionmaker(
            bind=self.__engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @property
    def engine(self):
        """
        Retorna o SQLAlchemy Engine.
        """

        return self.__engine

    def create_session(
        self,
    ) -> Session:
        """
        Cria uma nova sessão do banco.

        Returns:
            Session SQLAlchemy.
        """

        return self.__session_factory()

    def test_connection(
        self,
    ) -> None:
        """
        Testa a conexão com o banco de dados.

        Raises:
            Exception: Caso não seja possível conectar.
        """

        with self.__engine.connect() as connection:
            connection.exec_driver_sql(
                "SELECT 1"
            )

    def __create_engine(self):
        """
        Cria o SQLAlchemy Engine.
        """

        query = {
            "driver": self.__settings.driver,
            "TrustServerCertificate": (
                "yes"
                if self.__settings.trust_server_certificate
                else "no"
            ),
            "Encrypt": (
                "yes"
                if self.__settings.encrypt
                else "no"
            ),
        }

        if self.__settings.trusted_connection:
            query["Trusted_Connection"] = "yes"

        connection_url = URL.create(
            drivername="mssql+pyodbc",
            username=(
                self.__settings.username
                if not self.__settings.trusted_connection
                else None
            ),
            password=(
                self.__settings.password
                if not self.__settings.trusted_connection
                else None
            ),
            host=self.__settings.server,
            port=self.__settings.port,
            database=self.__settings.database,
            query=query,
        )

        return create_engine(
            connection_url,
            pool_pre_ping=True,
            connect_args={
                "timeout": (
                    self.__settings.connection_timeout
                ),
            },
        )