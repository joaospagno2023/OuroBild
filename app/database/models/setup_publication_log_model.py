"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_log_model.py
Descrição : Modelo SQLAlchemy dos logs de publicação de Setups.
--------------------------------------------------------------------
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SetupPublicationLogModel(Base):
    """Representa um evento persistido de publicação em lote."""

    __tablename__ = "SetupPublicationLogs"

    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column(
        "Id",
        primary_key=True,
        autoincrement=True,
    )

    batch_id: Mapped[str] = mapped_column(
        "BatchId",
        Unicode(64),
        ForeignKey(
            "dbo.SetupPublicationBatches.BatchId",
            ondelete="CASCADE",
        ),
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

    event_type: Mapped[str] = mapped_column(
        "EventType",
        Unicode(50),
        nullable=False,
    )

    project_id: Mapped[str | None] = mapped_column(
        "ProjectId",
        Unicode(100),
        nullable=True,
    )

    execution_id: Mapped[str | None] = mapped_column(
        "ExecutionId",
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
