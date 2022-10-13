from flask import jsonify
from flask.views import MethodView


class HealthCheckView(MethodView):
    """Service health check"""

    def get(self):
        return jsonify({"PING": "PONG"})
