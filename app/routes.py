from flask_restful import Api
from flask import Blueprint

from .views import MergeProfile

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Routes
api.add_resource(MergeProfile, '/merge-profiles/<profile_name>')