from datetime import datetime as dt
from datetime import timedelta as td

from flask import current_app as app
from sqlalchemy import Date, and_, asc, cast, func
from sqlalchemy.sql import select

from db import create_db_engine
from models.benefit import benefit
from models.benefit_usage import benefit_usage
from models.person import person
from models.venue import venue
from reporting.constants import (BENEFIT_INACTIVITY, BENEFIT_RECURRENCE,
                                 DATE_FORMAT, DATE_TIME_FORMAT)


def get_benefits():
    """Get benefits"""
    stmt = select(benefit).order_by(asc(benefit.c.id))
    with create_db_engine(app.config).connect() as conn:
        rows = conn.execute(stmt).all()

    return [dict(row) for row in rows]


def get_venue(venue_id):
    """Get venue object by id"""
    stmt = select(venue).where(venue.c.id == venue_id)
    with create_db_engine(app.config).connect() as conn:
        row = conn.execute(stmt).one_or_none()

    return dict(row) if row else None


def get_used_benefits(person_id, venue_id, date):
    """Get already used benefits for the user for a specific venue at the given time"""
    stmt = (
        select(
            [
                venue.c.id.label("venue_id"),
                benefit.c.id.label("benefit_id"),
                benefit.c.title.label("benefit_title"),
                benefit.c.recurrence.label("recurrence"),
                func.Max(benefit_usage.c.usageTimestamp).label("max_usage_time"),
            ]
        )
        .select_from(
            person.join(benefit_usage, person.c.id == benefit_usage.c.personId)
            .join(benefit, benefit.c.id == benefit_usage.c.benefitId)
            .join(venue, venue.c.id == benefit.c.venueId)
        )
        .group_by(
            person.c.id,
            venue.c.id,
            benefit.c.id,
            benefit.c.title,
            benefit.c.recurrence,
        )
        .having(
            and_(
                func.Max(cast(benefit_usage.c.usageTimestamp, Date)) <= date,
                person.c.id == person_id,
                venue.c.id == venue_id,
            )
        )
    )
    with create_db_engine(app.config).connect() as conn:
        rows = conn.execute(stmt).all()

    return [dict(row) for row in rows]


def find_available_benefits(used_benefits, date):
    """Find available benefits for the user"""
    available_benefits = []

    benefits = get_benefits()
    benefits_ids = [b["id"] for b in benefits]

    # find benefits that was never used
    unused_benefits = list(set(benefits_ids).difference([ub["benefit_id"] for ub in used_benefits]))
    if unused_benefits:
        for b in benefits:
            if b["id"] in unused_benefits:
                available_benefits.append(b)

    # find benefits that could be used
    for ub in used_benefits:
        recurrence = ub["recurrence"]
        delta = dt.strptime(date, DATE_FORMAT).date() - ub["max_usage_time"].date()
        if recurrence == "day" and delta.days < BENEFIT_RECURRENCE[recurrence]:
            continue
        elif recurrence == "week" and delta.days < BENEFIT_RECURRENCE[recurrence]:
            continue
        elif recurrence == "month" and delta.days < BENEFIT_RECURRENCE[recurrence]:
            continue
        else:
            (available_benefit,) = [b for b in benefits if b["id"] == ub["benefit_id"]]
            available_benefits.append(available_benefit)

    return available_benefits


def get_benefits_usage_by_venue(venue_id):
    """Get benefits usage by venue for the last 180 days"""
    _from = dt.now() - td(days=180)

    stmt = (
        select(
            [
                benefit_usage.c.benefitId.label("benefit_id"),
                benefit.c.recurrence.label("recurrence"),
                benefit_usage.c.usageTimestamp.label("usage_timestamp"),
            ]
        )
        .select_from(benefit_usage.join(benefit, benefit_usage.c.benefitId == benefit_usage.c.benefitId))
        .where(
            and_(
                benefit.c.venueId == venue_id,
                cast(benefit_usage.c.usageTimestamp, Date) > _from.date().strftime(DATE_FORMAT),
            )
        )
        .order_by(asc(benefit_usage.c.benefitId), asc(benefit_usage.c.usageTimestamp))
    )

    with create_db_engine(app.config).connect() as conn:
        rows = [dict(row) for row in conn.execute(stmt).all()]

    return rows


def get_inactivity_periods(benefits_usage):
    """Get inactivity periods of the benefits for specific venue"""
    inactivity_periods = []
    benefits_ids = [b["id"] for b in get_benefits()]

    for benefit_id in benefits_ids:
        inactive_time = []
        for idx, bu in enumerate(benefits_usage, start=1):
            try:
                if benefit_id != bu["benefit_id"] or benefit_id != benefits_usage[idx]["benefit_id"]:
                    continue
            except IndexError:
                break
            delta = benefits_usage[idx]["usage_timestamp"] - bu["usage_timestamp"]
            recurrence = bu["recurrence"]
            if delta.days >= BENEFIT_INACTIVITY[recurrence]:
                inactive_time.append(
                    {
                        "startTime": bu["usage_timestamp"].strftime(DATE_TIME_FORMAT),
                        "endTime": benefits_usage[idx]["usage_timestamp"].strftime(DATE_TIME_FORMAT),
                    }
                )

        if inactive_time:
            inactivity_periods.append({"benefitId": benefit_id, "inactivityPeriods": inactive_time})

    return inactivity_periods


def get_top_benefits():
    """Get top three benefits for every venue for the last 180 days"""
    _from = dt.now() - td(days=180)

    cte_benefit_count = (
        select(
            [benefit_usage.c.benefitId.label("benefit_id"), func.count(benefit_usage.c.benefitId).label("usage_count")]
        )
        .select_from(benefit_usage)
        .where(benefit_usage.c.usageTimestamp > _from.date().strftime(DATE_FORMAT))
        .group_by(
            benefit_usage.c.benefitId,
        )
        .cte("benefit_count")
    )

    cte_venue_benefits = (
        select(
            [
                benefit.c.id.label("benefit_id"),
                venue.c.name.label("venue_name"),
                venue.c.id.label("venue_id"),
                benefit.c.title.label("benefit_title"),
            ]
        )
        .select_from(venue.join(benefit, venue.c.id == benefit.c.venueId))
        .cte("venue_benefits")
    )

    cte_result_table = (
        select(
            [
                cte_venue_benefits.c.venue_id,
                cte_venue_benefits.c.venue_name,
                cte_venue_benefits.c.benefit_id,
                cte_benefit_count.c.usage_count,
                func.rank()
                .over(partition_by=cte_venue_benefits.c.venue_name, order_by=cte_benefit_count.c.usage_count)
                .label("rnk"),
            ]
        )
        .select_from(
            cte_benefit_count.join(
                cte_venue_benefits, cte_benefit_count.c.benefit_id == cte_venue_benefits.c.benefit_id
            )
        )
        .cte("result_table")
    )

    stmt = (
        select([cte_result_table.c.venue_id, cte_result_table.c.benefit_id, cte_result_table.c.usage_count])
        .select_from(cte_result_table)
        .where(cte_result_table.c.rnk <= 3)
        .order_by(asc(cte_result_table.c.venue_id), asc(cte_result_table.c.usage_count))
    )

    with create_db_engine(app.config).connect() as conn:
        rows = [dict(row) for row in conn.execute(stmt).all()]

    result = []
    venues = [r["venue_id"] for r in rows]
    for venue_id in venues:
        top_benefits = []
        for row in rows:
            if venue_id == row["venue_id"]:
                top_benefits.append({"benefitId": row["benefit_id"], "usageCount": row["usage_count"]})
        result.append({"venueId": venue_id, "topBenefits180Days": top_benefits})

    return result
