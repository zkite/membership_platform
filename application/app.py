from flask import Flask

from config import Development
from health import blueprint as health_blueprint
from reporting import blueprint as reporting_blueprint

app = Flask(Development.SERVICE_NAME)
app.config.from_object(Development)


app.register_blueprint(health_blueprint)
app.register_blueprint(reporting_blueprint)
