# config/utils.py

from urllib.parse import parse_qs, unquote, urlparse


def get_database_config_variables(url: str) -> dict:
    if not url:
        raise ValueError("DATABASE_URL environment variable must be set")

    parsed = urlparse(url)

    if not parsed.scheme or not parsed.hostname or not parsed.path:
        raise ValueError(f"Invalid DATABASE_URL: {url!r}")

    # Handle both postgres:// and postgresql://
    if parsed.scheme not in ("postgres", "postgresql"):
        raise ValueError(
            f"Unsupported database scheme in DATABASE_URL: {parsed.scheme!r}"
        )

    # Path is like "/dbname"
    db_name = parsed.path.lstrip("/") or None

    # Password & user may be percent-encoded
    username = unquote(parsed.username) if parsed.username else ""
    password = unquote(parsed.password) if parsed.password else ""

    # Optional connection options (?sslmode=require, etc.)
    query_params = parse_qs(parsed.query)

    return {
        "DATABASE_USER": username,
        "DATABASE_PASSWORD": password,
        "DATABASE_HOST": parsed.hostname,
        "DATABASE_PORT": str(parsed.port or ""),  # optionally default to 5432
        "DATABASE_NAME": db_name,
        "OPTIONS": query_params,  # you can map sslmode etc into DATABASES['OPTIONS']
    }
