from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.crypto import encrypt_secret
from app.models import Account, AccountCredential
from sqlalchemy import select


def create_account(db: Session, email: str) -> Account:
    existing = get_account_by_email(db, email)

    if existing is not None:
        raise ValueError("账号已存在")

    account = Account(email=email)

    db.add(account)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("账号已存在") from exc
    db.refresh(account)

    return account


def get_account_by_email(db: Session, email: str) -> Account | None:
    stmt = select(Account).where(Account.email == email)

    return db.scalar(stmt)


def create_account_credential(
    db: Session,
    account_id: int,
    password: str,
    two_fa: str,
) -> AccountCredential:
    account = db.get(Account, account_id)

    if account is None:
        raise ValueError("账号不存在")

    credential = AccountCredential(
        account_id=account_id,
        encrypted_password=encrypt_secret(password),
        encrypted_two_fa=encrypt_secret(two_fa),
        encrypted_refresh_token=None,
    )

    db.add(credential)

    try:
        db.commit()
    except IndentationError as exc:
        db.rollback()
        raise ValueError("账号凭据已存在") from exc

    db.refresh(credential)

    return credential


def get_account_credential(
    db: Session,
    account_id: int,
) -> AccountCredential | None:
    stmt = select(AccountCredential).where(AccountCredential.account_id == account_id)
    return db.scalar(stmt)
