from flask_cors import CORS
from flask import Flask

from routes import *

CORS(app)
app.register_blueprint(routes)


app.run(debug=True)


