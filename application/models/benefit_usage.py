from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, Table

from db import metadata
from models.benefit import benefit
from models.person import person

benefit_usage = Table(
    "benefit_usage",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("personId", Integer, ForeignKey(person.c.id), nullable=False),
    Column("benefitId", Integer, ForeignKey(benefit.c.id), nullable=False),
    Column("usageTimestamp", TIMESTAMP, nullable=False),
    schema="public",
)
