"""
Flask extensions — instantiated without app, bound later via init_app.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    default_limits=[],
    storage_uri="memory://"
)
