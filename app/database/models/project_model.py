"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_model.py
Descrição : Modelo SQLAlchemy da tabela de projetos.
--------------------------------------------------------------------
"""

from sqlalchemy import (
    Boolean,
    Unicode,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import (
    Base,
)


class ProjectModel(
    Base,
):
    """
    Representa a tabela de projetos do OuroBuild.
    """

    __tablename__ = "Projects"

    __table_args__ = {
        "schema": "dbo",
    }

    id: Mapped[str] = mapped_column(
        "Id",
        Unicode(100),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        "Name",
        Unicode(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        "Description",
        Unicode(),
        nullable=False,
    )

    type: Mapped[str] = mapped_column(
        "Type",
        Unicode(50),
        nullable=False,
    )

    solution_path: Mapped[str | None] = mapped_column(
        "SolutionPath",
        Unicode(1000),
        nullable=True,
    )

    project_path: Mapped[str | None] = mapped_column(
        "ProjectPath",
        Unicode(1000),
        nullable=True,
    )

    compilation_target: Mapped[str] = mapped_column(
        "CompilationTarget",
        Unicode(50),
        nullable=False,
    )

    compilation_engine: Mapped[str] = mapped_column(
        "CompilationEngine",
        Unicode(50),
        nullable=False,
    )

    publish_path: Mapped[str] = mapped_column(
        "PublishPath",
        Unicode(1000),
        nullable=False,
    )

    publish_profile: Mapped[str | None] = mapped_column(
        "PublishProfile",
        Unicode(200),
        nullable=True,
    )

    aip_path: Mapped[str] = mapped_column(
        "AipPath",
        Unicode(1000),
        nullable=False,
    )

    visualstudio_setup_path: Mapped[str | None] = mapped_column(
        "VisualStudioSetupPath",
        Unicode(1000),
        nullable=True,
    )

    output_msi: Mapped[str] = mapped_column(
        "OutputMsi",
        Unicode(1000),
        nullable=False,
    )

    network_path: Mapped[str] = mapped_column(
        "NetworkPath",
        Unicode(1000),
        nullable=False,
    )

    configuration: Mapped[str] = mapped_column(
        "Configuration",
        Unicode(100),
        nullable=False,
    )

    platform: Mapped[str] = mapped_column(
        "Platform",
        Unicode(100),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        "Enabled",
        Boolean,
        nullable=False,
    )