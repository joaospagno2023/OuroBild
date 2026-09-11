"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : cleanup_rule_model.py
Descrição : Modelo SQLAlchemy da tabela de regras de limpeza.
--------------------------------------------------------------------
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
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


class CleanupRuleModel(
    Base,
):
    """
    Representa a tabela de regras de limpeza.
    """

    __tablename__ = "CleanupRules"

    __table_args__ = {
        "schema": "dbo",
    }

    id: Mapped[int] = mapped_column(
        "Id",
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    project_id: Mapped[str | None] = mapped_column(
        "ProjectId",
        Unicode(100),
        nullable=True,
    )

    target: Mapped[str] = mapped_column(
        "Target",
        Unicode(30),
        nullable=False,
    )

    pattern: Mapped[str] = mapped_column(
        "Pattern",
        Unicode(1000),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        "Action",
        Unicode(30),
        nullable=False,
    )

    recursive: Mapped[bool] = mapped_column(
        "Recursive",
        Boolean,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        "Description",
        Unicode(2000),
        nullable=True,
    )

    priority: Mapped[int] = mapped_column(
        "Priority",
        Integer,
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        "Enabled",
        Boolean,
        nullable=False,
    )