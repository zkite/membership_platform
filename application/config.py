import os
from dataclasses import dataclass


@dataclass
class Development:
    SERVICE_NAME: str = "membership_platform"
    PG_USER: str = os.getenv("PG_USER")
    PG_PASS: str = os.getenv("PG_PASS")
    PG_HOST: str = os.getenv("PG_HOST")
    PG_PORT: str = os.getenv("PG_PORT")
    PG_NAME: str = os.getenv("PG_NAME")
    PG_ECHO: str = os.getenv("PG_ECHO", False)
