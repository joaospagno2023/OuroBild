"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : environment_model.py
Descrição : Modelo SQLAlchemy da tabela de ambientes.
--------------------------------------------------------------------
"""

from sqlalchemy import (
    Unicode,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import (
    Base,
)


class EnvironmentModel(
    Base,
):
    """
    Representa a tabela de ambientes do OuroBuild.
    """

    __tablename__ = "Environments"

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

    resolver: Mapped[str] = mapped_column(
        "Resolver",
        Unicode(50),
        nullable=False,
    )

    root_path: Mapped[str] = mapped_column(
        "RootPath",
        Unicode(1000),
        nullable=False,
    )