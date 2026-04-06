import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(encoding="utf-8")  # читает .env

@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5433"))
    db_name: str = os.getenv("DB_NAME", "diploma")
    db_user: str = os.getenv("DB_USER", "diploma")
    db_password: str = os.getenv("DB_PASSWORD", "diploma")

    its_crit: float = float(os.getenv("ITS_CRIT", "0.40"))
    degradation_p: float = float(os.getenv("DEGRADATION_P", "2.0"))

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()