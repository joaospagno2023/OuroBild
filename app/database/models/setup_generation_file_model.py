"""
--------------------------------------------------------------------
Projeto : OuroBuild

Arquivo : setup_generation_file_model.py

Descrição : Modelo SQLAlchemy dos arquivos produzidos durante
            uma geração de Setup.
--------------------------------------------------------------------
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SetupGenerationFileModel(Base):
    """
    Representa um arquivo produzido durante uma geração de Setup.
    """

    __tablename__ = "SetupGenerationFiles"
    __table_args__ = {"schema": "dbo"}

    id: Mapped[int] = mapped_column(
        "Id",
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    generation_id: Mapped[str] = mapped_column(
        "GenerationId",
        Unicode(100),
        nullable=False,
    )

    project_id: Mapped[str] = mapped_column(
        "ProjectId",
        Unicode(100),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        "FilePath",
        Unicode(1000),
        nullable=False,
    )

    generated_at: Mapped[datetime] = mapped_column(
        "GeneratedAt",
        DateTime,
        nullable=False,
    )

    success: Mapped[bool] = mapped_column(
        "Success",
        Boolean,
        nullable=False,
    )