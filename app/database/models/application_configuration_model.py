"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : application_configuration_model.py
Descrição : Modelo SQLAlchemy da configuração da aplicação.
--------------------------------------------------------------------
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    Unicode,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import (
    Base,
)


class ApplicationConfigurationModel(
    Base,
):
    """
    Representa a configuração persistida do OuroBuild.
    """

    __tablename__ = "ApplicationConfiguration"

    __table_args__ = {
        "schema": "dbo",
    }

    id: Mapped[int] = mapped_column(
        "Id",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    application_name: Mapped[str] = mapped_column(
        "ApplicationName",
        Unicode(200),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        "Version",
        Unicode(50),
        nullable=False,
    )

    log_level: Mapped[str] = mapped_column(
        "LogLevel",
        Unicode(20),
        nullable=False,
    )

    base_path: Mapped[str] = mapped_column(
        "BasePath",
        Unicode(1000),
        nullable=False,
    )

    installer_path: Mapped[str] = mapped_column(
        "InstallerPath",
        Unicode(1000),
        nullable=False,
    )

    publish_path: Mapped[str] = mapped_column(
        "PublishPath",
        Unicode(1000),
        nullable=False,
    )

    msbuild_path: Mapped[str] = mapped_column(
        "MsBuildPath",
        Unicode(1000),
        nullable=False,
    )

    advanced_installer_path: Mapped[str] = mapped_column(
        "AdvancedInstallerPath",
        Unicode(1000),
        nullable=False,
    )

    robocopy_path: Mapped[str] = mapped_column(
        "RobocopyPath",
        Unicode(1000),
        nullable=False,
    )

    setup_engine: Mapped[str] = mapped_column(
        "SetupEngine",
        Unicode(50),
        nullable=False,
    )

    setup_output_root: Mapped[str] = mapped_column(
        "SetupOutputRoot",
        Unicode(1000),
        nullable=False,
    )

    setup_aip_root: Mapped[str] = mapped_column(
        "SetupAipRoot",
        Unicode(2000),
        nullable=False,
    )

    setup_network_root_path: Mapped[str] = mapped_column(
        "SetupNetworkRootPath",
        Unicode(2000),
        nullable=False,
    )

    setup_excluir_pasta_work: Mapped[bool] = mapped_column(
        "SetupExcluirPastaWork",
        Boolean,
        nullable=False,
        default=False,
    )

    logging_enabled: Mapped[bool] = mapped_column(
        "LoggingEnabled",
        Boolean,
        nullable=False,
        default=True,
    )

    logging_path: Mapped[str] = mapped_column(
        "LoggingPath",
        Unicode(1000),
        nullable=False,
    )

    logging_level: Mapped[str] = mapped_column(
        "LoggingLevel",
        Unicode(20),
        nullable=False,
    )

    storage_workspace_path: Mapped[str] = mapped_column(
        "StorageWorkspacePath",
        Unicode(1000),
        nullable=False,
    )

    jwt_secret: Mapped[str] = mapped_column(
        "JwtSecret",
        Unicode(2000),
        nullable=False,
    )

    jwt_algorithm: Mapped[str] = mapped_column(
        "JwtAlgorithm",
        Unicode(50),
        nullable=False,
    )

    token_expiration_minutes: Mapped[int] = mapped_column(
        "TokenExpirationMinutes",
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        "CreatedAt",
        DateTime,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        "UpdatedAt",
        DateTime,
        nullable=False,
    )