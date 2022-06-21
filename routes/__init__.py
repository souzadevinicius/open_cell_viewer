"""
Application init routes
"""
import os
from flask import Blueprint
routes = Blueprint('routes', 'routes', static_folder=os.getcwd() + '/static', static_url_path='/public')


from .index import *
from .edge_detector_api import *
from .machine_learning_api import *

