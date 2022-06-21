from flask import Blueprint, Flask
from . import routes

@routes.route('/')
def root():
    return routes.send_static_file('index.html')