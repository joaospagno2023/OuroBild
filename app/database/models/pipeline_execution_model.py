"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_model.py
Descrição : Modelo SQLAlchemy da tabela de execuções da Pipeline.
--------------------------------------------------------------------
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Numeric,
    Unicode,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import (
    Base,
)


class PipelineExecutionModel(
    Base,
):
    """
    Representa a tabela de execuções da Pipeline.
    """

    __tablename__ = "PipelineExecutions"

    __table_args__ = {
        "schema": "dbo",
    }

    id: Mapped[int] = mapped_column(
        "Id",
        primary_key=True,
        autoincrement=True,
    )

    execution_id: Mapped[str] = mapped_column(
        "ExecutionId",
        Unicode(64),
        nullable=False,
    )

    session_id: Mapped[str] = mapped_column(
        "SessionId",
        Unicode(50),
        nullable=False,
    )

    project_id: Mapped[str] = mapped_column(
        "ProjectId",
        Unicode(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        "Status",
        Unicode(20),
        nullable=False,
    )

    success: Mapped[bool] = mapped_column(
        "Success",
        nullable=False,
    )

    message: Mapped[str | None] = mapped_column(
        "Message",
        Unicode(),
        nullable=True,
    )

    failed_step: Mapped[str | None] = mapped_column(
        "FailedStep",
        Unicode(200),
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        "StartedAt",
        DateTime,
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        "FinishedAt",
        DateTime,
        nullable=True,
    )

    elapsed_seconds: Mapped[float | None] = mapped_column(
        "ElapsedSeconds",
        Numeric(18, 3),
        nullable=True,
    )

    output_folder: Mapped[str | None] = mapped_column(
        "OutputFolder",
        Unicode(1000),
        nullable=True,
    )

    artifacts_json: Mapped[str | None] = mapped_column(
        "ArtifactsJson",
        Unicode(),
        nullable=True,
    )

    steps_json: Mapped[str | None] = mapped_column(
        "StepsJson",
        Unicode(),
        nullable=True,
    )

    build_json: Mapped[str | None] = mapped_column(
        "BuildJson",
        Unicode(),
        nullable=True,
    )

    publish_json: Mapped[str | None] = mapped_column(
        "PublishJson",
        Unicode(),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        "CreatedAt",
        DateTime,
        nullable=False,
    )

    version: Mapped[str | None] = mapped_column(
    "Version",
    Unicode(50),
    nullable=True,
)