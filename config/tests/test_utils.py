# config/tests/test_utils.py

import pytest

from config.utils import get_database_config_variables


def test_parses_basic_postgres_url_with_sslmode():
    url = "postgres://user:pass@localhost:5432/mydb?sslmode=require"

    cfg = get_database_config_variables(url)

    assert cfg["DATABASE_USER"] == "user"
    assert cfg["DATABASE_PASSWORD"] == "pass"
    assert cfg["DATABASE_HOST"] == "localhost"
    assert cfg["DATABASE_PORT"] == "5432"
    assert cfg["DATABASE_NAME"] == "mydb"
    # parse_qs returns lists
    assert cfg["OPTIONS"]["sslmode"] == ["require"]


def test_parses_postgresql_url_with_encoded_password_and_multiple_options():
    # password is "p@ss:w0rd" URL-encoded as p%40ss%3Aw0rd
    url = (
        "postgresql://myuser:p%40ss%3Aw0rd"
        "@db.example.com:6543/planit"
        "?sslmode=verify-full&connect_timeout=10"
    )

    cfg = get_database_config_variables(url)

    assert cfg["DATABASE_USER"] == "myuser"
    assert cfg["DATABASE_PASSWORD"] == "p@ss:w0rd"
    assert cfg["DATABASE_HOST"] == "db.example.com"
    assert cfg["DATABASE_PORT"] == "6543"
    assert cfg["DATABASE_NAME"] == "planit"
    assert cfg["OPTIONS"]["sslmode"] == ["verify-full"]
    assert cfg["OPTIONS"]["connect_timeout"] == ["10"]


def test_parses_url_without_port():
    # No explicit port -> parsed.port is None -> we store ""
    url = "postgres://user:pass@db.example.com/mydb"

    cfg = get_database_config_variables(url)

    assert cfg["DATABASE_HOST"] == "db.example.com"
    assert cfg["DATABASE_PORT"] == ""
    assert cfg["DATABASE_NAME"] == "mydb"
    assert cfg["DATABASE_USER"] == "user"
    assert cfg["DATABASE_PASSWORD"] == "pass"
    # No query string -> empty OPTIONS dict
    assert cfg["OPTIONS"] == {}


def test_raises_on_missing_url():
    with pytest.raises(ValueError) as excinfo:
        get_database_config_variables("")
    assert "DATABASE_URL environment variable must be set" in str(excinfo.value)


def test_raises_on_unsupported_scheme():
    url = "mysql://user:pass@localhost/db"

    with pytest.raises(ValueError) as excinfo:
        get_database_config_variables(url)
    assert "Unsupported database scheme in DATABASE_URL" in str(excinfo.value)


def test_raises_on_invalid_url_structure():
    # Missing hostname and path
    url = "postgres://"

    with pytest.raises(ValueError):
        get_database_config_variables(url)
