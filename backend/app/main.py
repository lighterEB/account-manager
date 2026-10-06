from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app import models
from app.account_parser import parse_account_content
from app.database import create_db_and_tables, get_db
from app.repository import create_account
from app.schema import AccountImportRequest, AccountImportResponse


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
            create_account(db, item["email"])
            success.append(item)

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
