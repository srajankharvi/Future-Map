"""
Blueprint registration — imports and registers all route blueprints.
"""


def register_blueprints(app):
    """Register all route blueprints on the Flask app."""
    from routes.auth import auth_bp
    from routes.careers import careers_bp
    from routes.courses import courses_bp
    from routes.interview import interview_bp
    from routes.projects import projects_bp
    from routes.recommendations import recommendations_bp
    from routes.roadmaps import roadmaps_bp
    from routes.search import search_bp
    from routes.yourpath import yourpath_bp
    from routes.static import static_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(careers_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(roadmaps_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(yourpath_bp)
    app.register_blueprint(static_bp)
