from datetime import datetime
import decimal
from typing import Literal
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.categorization import Categorization, CategorizationError, MissingOpenAIKey
from app.db.models import Transaction
from app.db.session import get_db

router = APIRouter()


class TransactionCreate(BaseModel):
    transaction_id: str = Field(min_length=1, max_length=50)
    amount: decimal.Decimal
    transaction_date: datetime
    description: str = Field(min_length=1, max_length=255)
    transaction_type: Literal["debit", "credit"]
    account_number: str = Field(min_length=1, max_length=255)


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    amount: decimal.Decimal
    transaction_date: datetime
    created_at: datetime | None
    description: str
    transaction_type: str
    account_number: str
    classification: int


categorizer = Categorization()


@router.get("/status", name="status")
async def status() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/transactions", response_model=TransactionRead, status_code=201)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
) -> Transaction:

    # Store the incoming transaction - "not-categories"
    # return immediately - fast post

    try:
        classification = categorizer.categorize(
            amount=transaction_data.amount,
            description=transaction_data.description,
            transaction_type=transaction_data.transaction_type,
        )
    except MissingOpenAIKey as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except CategorizationError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    transaction = Transaction(**transaction_data.model_dump(), classification=classification)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

# scheduled job "not categorised" > categorises
# batching / semaphore / async processing
# description / similar or account numbers - probably categorized / lookup / cache

@router.get("/transactions", response_model=list[TransactionRead])
def get_transactions(
    classification: int | None = None,
    transaction_type: Literal["debit", "credit"] | None = None,
    account_number: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    search: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Transaction]:
    # if min_amount is not None and max_amount is not None and min_amount > max_amount:
    #     raise HTTPException(status_code=422, detail="min_amount must not exceed max_amount")
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must not exceed end_date")

    statement = select(Transaction)
    if classification is not None:
        statement = statement.where(Transaction.classification == classification)
    if transaction_type is not None:
        statement = statement.where(Transaction.transaction_type == transaction_type)
    if account_number is not None:
        statement = statement.where(Transaction.account_number == account_number)
    if start_date is not None:
        statement = statement.where(Transaction.transaction_date >= start_date)
    if end_date is not None:
        statement = statement.where(Transaction.transaction_date <= end_date)
    if search is not None:
        statement = statement.where(Transaction.description.ilike(f"%{search}%"))

    statement = statement.order_by(Transaction.transaction_date.desc()).limit(limit).offset(offset)
    return list(db.scalars(statement))


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction