"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : base.py
Descrição : Define a base dos modelos SQLAlchemy.
--------------------------------------------------------------------
"""

from sqlalchemy.orm import (
    DeclarativeBase,
)


class Base(
    DeclarativeBase,
):
    """
    Base declarativa utilizada pelos modelos SQLAlchemy.
    """

    pass