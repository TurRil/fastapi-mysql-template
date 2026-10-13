from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Integer, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, server_default=func.current_timestamp()
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    transaction_type: Mapped[str] = mapped_column(
        Enum("debit", "credit", name="transaction_type"), nullable=False
    )
    account_number: Mapped[str] = mapped_column(String(255), nullable=False)
    classification: Mapped[int] = mapped_column(Integer, nullable=False, default=0)