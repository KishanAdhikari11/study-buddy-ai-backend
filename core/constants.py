class Validation:
    """Validation rules and constraints"""

    MIN_PASSWORD_LENGTH = 8


class OAuth:
    """OAUTH provider constants"""

    GOOGLE = "google"


class Supabase:
    """Supabase specific constants"""

    REQUIRED_SECRETS = ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_JWT_SECRET"]
    FULL_NAME_FIELD = "full_name"
