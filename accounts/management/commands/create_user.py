# accounts/management/commands/create_user.py
"""
Management command: create_user

Create a superuser and/or a regular user from environment variables, with the
option to update an existing user (email/password/flags) if they already exist.

Typical use cases
-----------------
- Local/dev bootstrap: quickly seed a project with a known admin + demo user.
- CI pipelines: create accounts before running integration tests.
- One-off ops: update credentials or flags on an existing user via --update-existing.

Environment variables
---------------------
Superuser (SU_VARS)
- DJANGO_SU_NAME       (required)  -> username
- DJANGO_SU_EMAIL      (optional)  -> email
- DJANGO_SU_PASSWORD   (optional)  -> password

Regular user (USER_VARS)
- DJANGO_USER_NAME     (required)  -> username
- DJANGO_USER_EMAIL    (optional)  -> email
- DJANGO_USER_PASSWORD (optional)  -> password
- DJANGO_USER_ACCEPTED (optional)  -> "1"/"0" for `registration_accepted` (custom field)
- DJANGO_USER_IS_STAFF (optional)  -> "1"/"0" for `is_staff`

CLI options
-----------
--create {su|user|both}   Which account(s) to create. Default: both
--update-existing         If the username already exists, update fields from env
--dotenv PATH             Path to .env (default: project_root/.env)

Behavior notes
--------------
- Idempotent: Creating the same username twice does not duplicate accounts.
- Updating: With --update-existing, only provided values are changed.
- Superuser always enforces is_superuser=True, is_staff=True, and
  registration_accepted=True (if the custom field exists).
- Regular user explicitly sets is_superuser=False.

Security notes
--------------
- Avoid committing real credentials to .env in version control.
- Prefer per-env .env files and a secret manager in production.
- If a password is omitted, Django will create a *usable* password only if
  provided. Passing None sets an unusable password (cannot log in via password).

Exit behavior
-------------
- Raises CommandError if the .env file is missing or required variables are absent.
- Prints human-friendly messages for created/updated/no-op cases.

Examples
--------
# Create both users from project .env
python manage.py create_user

# Create only a superuser
python manage.py create_user --create su

# Update an existing user with the values currently in .env
python manage.py create_user --create user --update-existing

# Use a different .env path
python manage.py create_user --dotenv ./config/local.env
"""
import os
from pathlib import Path
from typing import Dict, Tuple

import dotenv
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Guess the project root: .../accounts/management/commands -> parents[3]
# This lets us default to project_root/.env while still allowing --dotenv override.
ENV_ROOT = Path(__file__).resolve().parents[3]
DOTENV_PATH = ENV_ROOT / ".env"

# Map the semantic field names we care about to their environment variable names.
# These mappings drive _read_env() so adding/removing envs is centralized.
SU_VARS = {
    "username": "DJANGO_SU_NAME",
    "email": "DJANGO_SU_EMAIL",
    "password": "DJANGO_SU_PASSWORD",
}
USER_VARS = {
    "username": "DJANGO_USER_NAME",
    "email": "DJANGO_USER_EMAIL",
    "password": "DJANGO_USER_PASSWORD",
    # Optional toggles for your custom fields in dev
    "accepted": "DJANGO_USER_ACCEPTED",  # "1" or "0" -> registration_accepted
    "staff": "DJANGO_USER_IS_STAFF",  # "1" or "0" -> is_staff
}


class Command(BaseCommand):
    """
    Django management command entry point. See module docstring for full docs.
    """

    help = "Create users from .env variables (superuser and/or regular user)."

    def add_arguments(self, parser):
        """
        Define CLI flags:
        --create           Choose what to create
        --update-existing  If a username exists, update its fields from env
        --dotenv           Path to .env file to load
        """
        parser.add_argument(
            "--create",
            choices=["su", "user", "both"],
            default="both",
            help="What to create from env vars (default: both).",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="If user already exists, update email and password from env.",
        )
        parser.add_argument(
            "--dotenv",
            default=str(DOTENV_PATH),
            help="Path to .env (default: project_root/.env).",
        )

    def handle(self, *args, **options):
        """
        Command runner:
        1) Load .env
        2) Create/update superuser and/or regular user based on --create
        3) Print a summary/no-op message
        """
        # 1) Load .env from the selected path
        dotenv_path = Path(options["dotenv"])
        if dotenv_path.exists():
            dotenv.load_dotenv(dotenv_path)
        else:
            # Fail fast so CI/devs know the source of truth for credentials wasn't found
            raise CommandError(f".env file not found at {dotenv_path}")

        created_anything = False

        # 2) Create or update a superuser if requested
        if options["create"] in ("su", "both"):
            created_anything |= self._create_superuser(
                update_existing=options["update_existing"]
            )

        # 3) Create or update a regular user if requested
        if options["create"] in ("user", "both"):
            created_anything |= self._create_regular_user(
                update_existing=options["update_existing"]
            )

        # 4) If neither branch did anything, say so to avoid silent runs
        if not created_anything:
            self.stdout.write(self.style.WARNING("Nothing to do."))

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────
    def _read_env(self, mapping: Dict[str, str]) -> Tuple[str, str, str, Dict]:
        """
        Extract credential fields from environment variables per the provided mapping.

        Returns
        -------
        (username, email, password, extras)
          - username: str  (required; CommandError if missing)
          - email:    str  (optional; empty string if unset)
          - password: str  (optional; empty string if unset)
          - extras:   dict (optional feature flags; see notes below)

        Notes
        -----
        For regular users, we also look for:
        - DJANGO_USER_ACCEPTED -> registration_accepted (bool)
        - DJANGO_USER_IS_STAFF -> is_staff (bool)
        """
        username = os.getenv(mapping["username"]) or ""
        email = os.getenv(mapping["email"]) or ""
        password = os.getenv(mapping["password"]) or ""
        if not username:
            # Username is the unique key we operate on; without it we can't proceed.
            raise CommandError(f"{mapping['username']} not set")

        extras = {}
        # Optional toggles for regular users (or any mapping that declares them).
        if "accepted" in mapping:
            extras["registration_accepted"] = os.getenv(mapping["accepted"], "1") == "1"
        if "staff" in mapping:
            extras["is_staff"] = os.getenv(mapping["staff"], "0") == "1"

        return username, email, password, extras

    @transaction.atomic
    def _ensure_user(
        self,
        *,
        username: str,
        email: str,
        password: str,
        update_existing: bool,
        **extra_fields,
    ):
        """
        Create or update a user with the given username.

        If the user exists:
          - With --update-existing: selectively update email/password/extra flags
          - Without --update-existing: print a warning and do nothing

        If the user does not exist:
          - Create a new user via User.objects.create_user()

        Returns
        -------
        bool
            True  -> a new user was created
            False -> user existed (maybe updated, maybe no-op)
        """
        User = get_user_model()
        qs = User.objects.filter(username=username)

        if qs.exists():
            # User exists: optionally update selected fields
            user = qs.get()
            if update_existing:
                changed = False

                # Update email only if a new non-empty value was provided
                if email and user.email != email:
                    user.email = email
                    changed = True

                # Update booleans from extra_fields (e.g., is_staff, registration_accepted) # noqa: E501
                for k, v in extra_fields.items():
                    if v is not None and getattr(user, k, None) != v:
                        setattr(user, k, v)
                        changed = True

                # Update password if provided (set_password handles hashing)
                if password:
                    user.set_password(password)
                    changed = True

                if changed:
                    # save(update_fields=None) => save all fields with tracked changes
                    user.save(update_fields=None)
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated existing user '{username}'")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"No changes for existing user '{username}'")
                    )
            else:
                # User exists and we were asked NOT to update: tell the operator how to proceed # noqa: E501
                self.stdout.write(
                    self.style.WARNING(
                        f"User '{username}' already exists. "
                        f"(use --update-existing to modify)"
                    )
                )
            return False  # not created

        # New user path: create_user respects password=None => sets unusable password
        user = User.objects.create_user(
            username=username,
            email=email or "",
            password=password or None,
            **extra_fields,
        )
        # If you have additional required fields in a custom user, ensure they are
        # passed via `extra_fields` (fed from env) before saving above.
        self.stdout.write(self.style.SUCCESS(f"Created user '{username}'"))
        return True  # created

    def _create_superuser(self, *, update_existing: bool) -> bool:
        """
        Read SU env vars and ensure the account has superuser/staff/accepted flags.
        """
        username, email, password, extras = self._read_env(SU_VARS)
        extras.update(
            {"is_superuser": True, "is_staff": True, "registration_accepted": True}
        )
        # If an existing user isn't a superuser, --update-existing will elevate it.
        return self._ensure_user(
            username=username,
            email=email,
            password=password,
            update_existing=update_existing,
            **extras,
        )

    def _create_regular_user(self, *, update_existing: bool) -> bool:
        """
        Read regular-user env vars and ensure is_superuser is False by design.
        """
        username, email, password, extras = self._read_env(USER_VARS)
        extras.update({"is_superuser": False})
        return self._ensure_user(
            username=username,
            email=email,
            password=password,
            update_existing=update_existing,
            **extras,
        )
