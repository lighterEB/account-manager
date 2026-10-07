from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app import models
from app.account_parser import parse_account_content
from app.database import create_db_and_tables, get_db
from app.schema import AccountImportRequest, AccountImportResponse

from app.crypto import decrypt_secret
from app.repository import (
    create_account_with_credential,
    list_account_with_credentials,
)

from app.schema import (
    AccountImportRequest,
    AccountImportResponse,
    AccountListItem,
)

from app.totp import generate_totp

app = FastAPI()
create_db_and_tables()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/accounts/import",
    response_model=AccountImportResponse,
)
def import_accounts(
    request: AccountImportRequest,
    db: Session = Depends(get_db),
):
    result = parse_account_content(request.content)

    success = []
    errors = list(result["errors"])

    for item in result["success"]:
        try:
            create_account_with_credential(
                db,
                email=item["email"],
                password=item["password"],
                two_fa=item["two_fa"],
            )
            success.append(
                {
                    "line": item["line"],
                    "email": item["email"],
                    "totp_code": item["totp_code"],
                }
            )

        except ValueError as exc:
            errors.append(
                {
                    "line": item["line"],
                    "message": str(exc),
                }
            )
    return {
        "success": success,
        "errors": errors,
    }


@app.get(
    "/accounts",
    response_model=list[AccountListItem],
)
def list_accounts(db: Session = Depends(get_db)):
    rows = list_account_with_credentials(db)

    result = []

    for account, credential in rows:
        two_fa = decrypt_secret(credential.encrypted_two_fa)
        totp_code = generate_totp(two_fa)

        result.append(
            {
                "id": account.id,
                "email": account.email,
                "status": account.status,
                "totp_code": totp_code,
                "created_at": account.created_at,
            }
        )

    return result
