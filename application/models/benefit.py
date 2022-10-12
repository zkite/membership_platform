from sqlalchemy import Column, ForeignKey, Integer, String, Table

from db import metadata
from models.venue import venue

benefit = Table(
    "benefit",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("venueId", Integer, ForeignKey(venue.c.id), nullable=False),
    Column("title", String, nullable=False),
    Column("recurrence", String, nullable=False),
    schema="public",
)
