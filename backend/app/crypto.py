import os

from cryptography.fernet import Fernet


def get_fernet() -> Fernet:
    key = os.environ.get("ACCOUNT_MANAGER_MASTER_KEY")

    if not key:
        raise RuntimeError("ACCOUNT_MANAGER_MASTER_KEY 未配置")

    return Fernet(key.encode())


def encrypt_secret(value: str) -> str:
    return get_fernet().encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    return get_fernet().decrypt(value.encode()).decode()
