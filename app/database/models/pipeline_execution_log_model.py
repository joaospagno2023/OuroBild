"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_execution_log_model.py
Descrição : Modelo SQLAlchemy da tabela de logs das execuções
             da Pipeline.
--------------------------------------------------------------------
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Unicode,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import (
    Base,
)


class PipelineExecutionLogModel(
    Base,
):
    """
    Representa a tabela de logs das execuções da Pipeline.
    """

    __tablename__ = "PipelineExecutionLogs"

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

    timestamp: Mapped[datetime] = mapped_column(
        "Timestamp",
        DateTime,
        nullable=False,
    )

    level: Mapped[str] = mapped_column(
        "Level",
        Unicode(20),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        "Source",
        Unicode(100),
        nullable=True,
    )

    message: Mapped[str] = mapped_column(
        "Message",
        Unicode(),
        nullable=False,
    )

    details: Mapped[str | None] = mapped_column(
        "Details",
        Unicode(),
        nullable=True,
    )