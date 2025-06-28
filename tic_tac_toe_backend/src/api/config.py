# config.py - Settings and environment loading for Tic Tac Toe backend

import os
from dotenv import load_dotenv


# PUBLIC_INTERFACE
class Settings:
    """App settings loaded from environment variables."""
    def __init__(self):
        # Load .env in project root, fallback to environment if missing
        load_dotenv()
        self.db_url = (
            os.getenv("POSTGRES_URL")
            or "postgresql://postgres:postgres@localhost:5432/tic_tac_toe"
        )
        self.db_user = os.getenv("POSTGRES_USER", "postgres")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.db_name = os.getenv("POSTGRES_DB", "tic_tac_toe")
        self.db_port = os.getenv("POSTGRES_PORT", "5432")
        self.secret_key = os.getenv("SECRET_KEY", "changeme-super-secret")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )
        self.env = os.getenv("ENV", "development")

    # PUBLIC_INTERFACE
    def sqlalchemy_db_uri(self):
        """Synthesizes full DB URI from components."""
        if "postgresql://" in self.db_url:
            return self.db_url
        return (
            f"postgresql://{self.db_user}:{self.db_password}@localhost:"
            f"{self.db_port}/{self.db_name}"
        )


settings = Settings()
