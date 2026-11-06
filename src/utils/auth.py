import hashlib
import hmac
import secrets

ITERACOES = 100_000


def hash_senha(senha):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), bytes.fromhex(salt), ITERACOES
    )
    return f"{salt}${digest.hex()}"


def verificar_senha(senha, senha_hash):
    try:
        salt, digest_hex = senha_hash.split("$", 1)
        digest = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), bytes.fromhex(salt), ITERACOES
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, AttributeError, TypeError):
        return False


def validar_senha(senha):
    if len(senha) < 6:
        raise ValueError("A senha deve ter pelo menos 6 caracteres.")
