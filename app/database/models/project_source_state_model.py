"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_source_state_model.py
Descrição : Modelo SQLAlchemy do estado dos fontes do projeto.
--------------------------------------------------------------------
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ProjectSourceStateModel(Base):
    """Representa a tabela dbo.ProjectSourceStates."""

    __tablename__ = "ProjectSourceStates"

    __table_args__ = {
        "schema": "dbo",
    }

    id: Mapped[int] = mapped_column(
        "Id",
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    project_id: Mapped[str] = mapped_column(
        "ProjectId",
        Unicode(100),
        nullable=False,
        unique=True,
    )

    source_hash: Mapped[str] = mapped_column(
        "SourceHash",
        Unicode(64),
        nullable=False,
    )

    last_checked_at: Mapped[datetime | None] = mapped_column(
        "LastCheckedAt",
        DateTime,
        nullable=True,
    )

    last_get_last_at: Mapped[datetime | None] = mapped_column(
        "LastGetLastAt",
        DateTime,
        nullable=True,
    )

    last_build_at: Mapped[datetime | None] = mapped_column(
        "LastBuildAt",
        DateTime,
        nullable=True,
    )
