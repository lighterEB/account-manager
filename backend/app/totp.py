import binascii
import base64
import re
from urllib.parse import parse_qs, unquote, urlparse

import pyotp


def normalize_totp_secret(value: str) -> str:
    value = value.strip()

    parsed = urlparse(value)

    # otpauth://totp/...?secret=XXXX
    if parsed.scheme == "otpauth":
        params = parse_qs(parsed.query)
        values = params.get("secret")

        if not values:
            raise ValueError("2FA URL 中没有 Secret")
        secret = values[0]

    # 任意 http/https URL
    elif parsed.scheme in {"htpp", "https"}:
        params = parse_qs(parsed.query)

        secret = None

        for key in ("secret", "token", "key"):
            values = params.get(key)

            if values:
                secret = values[0]
                break

        # 查询参数没有就取URL最后一段
        if secret is None:
            secret = unquote(parsed.path.rstrip("/").split("/")[-1])

    # 本身就是Secret
    else:
        secret = value

    secret = re.sub(r"[\s-]+", "", secret).upper()
    secret = secret.rstrip("=")

    if not re.fullmatch(r"[A-Z2-7]+", secret):
        raise ValueError("2FA Secret 格式无效")

    try:
        padding = "=" * ((8 - len(secret) % 8) % 8)
        base64.b32decode(secret + padding, casefold=True)
    except binascii.Error as exc:
        raise ValueError("2FA Secret 格式无效") from exc
    return secret


def generate_totp(secret: str) -> str:
    secret = normalize_totp_secret(secret)

    try:
        return pyotp.TOTP(secret).now()
    except (ValueError, binascii.Error) as exc:
        raise ValueError("2FA Secret 格式无效2FA Secret 格式无效") from exc
