"""
Flask extensions — instantiated without app, bound later via init_app.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys

mongo_uri = os.getenv('MONGODB_URL') or os.getenv('MONGODB_URI')

# Force in-memory storage for rate limiting during testing to prevent network-dependent failures
if "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST") or (len(sys.argv) > 0 and "pytest" in sys.argv[0]):
    storage_uri = "memory://"
else:
    storage_uri = mongo_uri if mongo_uri else "memory://"

limiter = Limiter(
    get_remote_address,
    default_limits=[],
    storage_uri=storage_uri
)
