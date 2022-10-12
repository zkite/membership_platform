from datetime import datetime as dt
from http import HTTPStatus

from flask import jsonify, request
from flask.views import MethodView

from reporting.core import (find_available_benefits,
                            get_benefits_usage_by_venue,
                            get_inactivity_periods, get_top_benefits,
                            get_used_benefits, get_venue)


class TopBenefitsView(MethodView):
    """Three most used benefits for every venue during the last 180 days"""

    def get(self):
        return jsonify(get_top_benefits())


class VenuesBenefitsView(MethodView):
    """Available benefits for the user for a specific venue at the given time"""

    def get(self, venue_id):
        date = request.args.get("date", dt.utcnow())
        person_id = request.args.get("person_id")

        if not person_id:
            return "person_id argument is required", HTTPStatus.BAD_REQUEST
        if not get_venue(venue_id):
            return "Venue not found", HTTPStatus.NOT_FOUND

        used_benefits = get_used_benefits(person_id=person_id, venue_id=venue_id, date=date)
        available_benefits = find_available_benefits(used_benefits=used_benefits, date=date)

        return jsonify(available_benefits)


class InactivityBenefitsPeriodsView(MethodView):
    """lists of the inactivity periods of the
    benefits for the specific venue which have had inactivity
    periods during the last 180 days."""

    def get(self, venue_id):
        benefits_usage = get_benefits_usage_by_venue(venue_id)
        inactivity_periods = get_inactivity_periods(benefits_usage)

        return jsonify(inactivity_periods)
