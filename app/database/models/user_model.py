"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : user_model.py
Descrição : Modelo SQLAlchemy da tabela de usuários.
--------------------------------------------------------------------
"""

from datetime import (
    datetime,
    timezone,
)

from sqlalchemy import (
    Boolean,
    DateTime,
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


class UserModel(
    Base,
):
    """
    Representa a tabela de usuários do OuroBuild.
    """

    __tablename__ = "Users"

    __table_args__ = {
        "schema": "dbo",
    }

    id: Mapped[int] = mapped_column(
        "Id",
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    username: Mapped[str] = mapped_column(
        "Username",
        Unicode(100),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        "PasswordHash",
        Unicode(500),
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        "DisplayName",
        Unicode(150),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        "Email",
        Unicode(254),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        "IsActive",
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        "CreatedAt",
        DateTime,
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc,
        ),
    )

    last_login_at: Mapped[datetime | None] = (
        mapped_column(
            "LastLoginAt",
            DateTime,
            nullable=True,
        )
    )