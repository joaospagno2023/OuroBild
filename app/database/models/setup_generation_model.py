from datetime import datetime

from sqlalchemy import DateTime, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SetupGenerationModel(Base):
    __tablename__ = "SetupGenerations"
    __table_args__ = {"schema": "dbo"}

    generation_id: Mapped[str] = mapped_column(
        "GenerationId", Unicode(100), primary_key=True
    )

    version: Mapped[str | None] = mapped_column(
        "Version", Unicode(100), nullable=True
    )

    revision: Mapped[int | None] = mapped_column(
        "Revision", Integer, nullable=True
    )

    environment_id: Mapped[str] = mapped_column(
        "EnvironmentId", Unicode(100), nullable=False
    )

    status: Mapped[str] = mapped_column(
        "Status", Unicode(50), nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        "StartedAt", DateTime, nullable=False
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        "FinishedAt", DateTime, nullable=True
    )

    last_file_path: Mapped[str | None] = mapped_column(
        "LastFilePath", Unicode(1000), nullable=True
    )

    last_file_generated_at: Mapped[datetime | None] = mapped_column(
        "LastFileGeneratedAt", DateTime, nullable=True
    )

    validity_minutes: Mapped[int] = mapped_column(
        "ValidityMinutes", Integer, nullable=False
    )

    created_by: Mapped[str | None] = mapped_column(
        "CreatedBy", Unicode(200), nullable=True
    )

    execution_id: Mapped[str | None] = mapped_column(
        "ExecutionId", Unicode(64), nullable=True
    )