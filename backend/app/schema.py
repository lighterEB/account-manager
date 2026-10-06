from pydantic import BaseModel


class AccountImportRequest(BaseModel):
    content: str


class AccountImportItem(BaseModel):
    line: int
    email: str
    # password: str
    # two_fa: str
    totp_code: str


class AccountImportError(BaseModel):
    line: int
    message: str


class AccountImportResponse(BaseModel):
    success: list[AccountImportItem]
    errors: list[AccountImportError]
