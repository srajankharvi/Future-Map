"""
Flask extensions — instantiated without app, bound later via init_app.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

mongo_uri = os.getenv('MONGODB_URL') or os.getenv('MONGODB_URI')
storage_uri = mongo_uri if mongo_uri else "memory://"

limiter = Limiter(
    get_remote_address,
    default_limits=[],
    storage_uri=storage_uri
)
