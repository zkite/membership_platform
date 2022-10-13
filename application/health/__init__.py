from flask import Blueprint

from health import views as health_check_view

blueprint = Blueprint("health", __name__, url_prefix="/")

blueprint.add_url_rule("/health", view_func=health_check_view.HealthCheckView.as_view("health_check"))