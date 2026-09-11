"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_batch_model.py
Descrição : Modelo SQLAlchemy das publicações em lote de Setups.
--------------------------------------------------------------------
"""

from datetime import datetime

from sqlalchemy import DateTime, Numeric, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SetupPublicationBatchModel(Base):
    """Representa a tabela de publicações em lote de Setups."""

    __tablename__ = "SetupPublicationBatches"

    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column(
        "Id",
        primary_key=True,
        autoincrement=True,
    )

    batch_id: Mapped[str] = mapped_column(
        "BatchId",
        Unicode(64),
        nullable=False,
        unique=True,
    )

    version: Mapped[str] = mapped_column(
        "Version",
        Unicode(50),
        nullable=False,
    )

    revision: Mapped[int] = mapped_column(
        "Revision",
        nullable=False,
    )

    source_path: Mapped[str] = mapped_column(
        "SourcePath",
        Unicode(1000),
        nullable=False,
    )

    destination_path: Mapped[str | None] = mapped_column(
        "DestinationPath",
        Unicode(2000),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        "Status",
        Unicode(30),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        "StartedAt",
        DateTime,
        nullable=False,
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

    total_setups: Mapped[int] = mapped_column(
        "TotalSetups",
        nullable=False,
    )

    completed_setups: Mapped[int] = mapped_column(
        "CompletedSetups",
        nullable=False,
    )

    failed_setups: Mapped[int] = mapped_column(
        "FailedSetups",
        nullable=False,
    )

    message: Mapped[str | None] = mapped_column(
        "Message",
        Unicode(),
        nullable=True,
    )
