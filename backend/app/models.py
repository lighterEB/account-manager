from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="IMPORTED",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
    )


class AccountCredential(Base):
    __tablename__ = "account_credentials"

    id: Mapped[int] = mapped_column(primary_key=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    encrypted_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    encrypted_two_fa: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    encrypted_refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
    )
