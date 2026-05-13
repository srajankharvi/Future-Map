"""
Vercel serverless function entry point.
This is a thin wrapper that imports the Flask app from the project root.
Vercel's @vercel/python runtime looks for an `app` variable here.
"""

import sys
import os

# Add the project root to Python's path so all imports (config, routes, etc.) work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
