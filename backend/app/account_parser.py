from app.totp import generate_totp

DELIMITER = "----"
TWO_FA_PREFIX = "https://2fa.live/tok/"


def parse_account_line(line: str) -> tuple[str, str, str]:
    line = line.strip()

    first = line.find(DELIMITER)
    last = line.rfind(DELIMITER)

    if first == -1 or last == -1 or first == last:
        raise ValueError("账号格式不正确")

    email = line[:first].strip()
    password = line[first + len(DELIMITER) : last]
    two_fa = parse_two_fa(line[last + len(DELIMITER) :])

    if not email or not password or not two_fa:
        raise ValueError("账号、密码和 2AF 都不能为空")

    return email, password, two_fa


def parse_account_content(content: str) -> dict:
    success = []
    errors = []

    for line_no, line in enumerate(content.splitlines(), start=1):
        line = line.strip()

        if not line:
            continue

        try:
            email, password, two_fa = parse_account_line(line)
            totp_code = generate_totp(two_fa)
            success.append(
                {
                    "line": line_no,
                    "email": email,
                    "password": password,
                    "two_fa": two_fa,
                    "totp_code": totp_code,
                }
            )
        except ValueError as exc:
            errors.append(
                {
                    "line": line_no,
                    "message": str(exc),
                }
            )

    return {
        "success": success,
        "errors": errors,
    }


def parse_two_fa(value: str) -> str:
    value = value.strip()

    if value.startswith(TWO_FA_PREFIX):
        value = value[len(TWO_FA_PREFIX) :]

    if not value:
        raise ValueError("2FA secrete 不能为空")

    return value
