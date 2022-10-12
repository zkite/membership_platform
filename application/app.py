from flask import Flask

from config import Development
from reporting import blueprint as reporting_blueprint

app = Flask(Development.SERVICE_NAME)
app.config.from_object(Development)


app.register_blueprint(reporting_blueprint)
