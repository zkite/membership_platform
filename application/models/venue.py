from sqlalchemy import Column, Integer, String, Table

from db import metadata

venue = Table(
    "venue",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    schema="public",
)
