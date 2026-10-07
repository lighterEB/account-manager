import re

from app.totp import generate_totp, normalize_totp_secret


DELIMITER = "----"
RECORD_PREFIX_PATTERN = re.compile(r"^\s*[^:：\r\n]{0,32}?\d+[^:：\r\n]{0,16}[:：]\s*")


def parse_account_line(line: str) -> tuple[str, str, str]:
    line = normalize_account_line(line)
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

        if not looks_like_account_record(line):
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
    return normalize_totp_secret(value)


def normalize_account_line(line: str) -> str:
    line = line.strip()

    return RECORD_PREFIX_PATTERN.sub("", line, count=1)


def looks_like_account_record(line: str) -> bool:
    line = normalize_account_line(line)

    first = line.find(DELIMITER)
    last = line.rfind(DELIMITER)

    # 至少必须有两个 ----
    if first == -1 or last == -1 or first == last:
        return False

    two_fa = line[last + len(DELIMITER) :].strip()

    if not two_fa:
        return False

    # URL 类型的 2FA
    if two_fa.startswith(("http://", "https://", "otpauth://")):
        return True

    # 裸 Secret 通常不会短
    return len(two_fa) >= 16
