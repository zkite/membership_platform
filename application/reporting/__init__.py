from flask import Blueprint

from reporting import views as reporting_views

blueprint = Blueprint("reporting", __name__, url_prefix="/reports")

blueprint.add_url_rule("/benefits/top", view_func=reporting_views.TopBenefitsView.as_view("top_benefits"))
blueprint.add_url_rule(
    "/venues/<int:venue_id>/benefits", view_func=reporting_views.VenuesBenefitsView.as_view("venues_benefits")
)
blueprint.add_url_rule(
    "/venues/<int:venue_id>/benefits/inactive",
    view_func=reporting_views.InactivityBenefitsPeriodsView.as_view("inactivity_benefits"),
)
