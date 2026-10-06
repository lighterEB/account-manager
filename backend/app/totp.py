import binascii

import pyotp


def generate_totp(secret: str) -> str:
    try:
        return pyotp.TOTP(secret).now()
    except (ValueError, binascii.Error) as exc:
        raise ValueError("2FA Secret 格式无效2FA Secret 格式无效") from exc
