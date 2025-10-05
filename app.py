"""Flask application entry point"""
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models import db
import os


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"⚠️  Configuration error: {e}")
        print("⚠️  Please set required environment variables in .env file")

    # CORS configuration - environment specific
    if os.getenv('FLASK_ENV') == 'production':
        # Production: restrict to Azure app
        app_name = Config.APP_NAME
        allowed_origins = [f"https://{app_name}.azurewebsites.net"]
        CORS(app, origins=allowed_origins)
    else:
        # Development: allow localhost
        CORS(app, origins=["http://localhost:5000", "http://127.0.0.1:5000"])

    # Initialize database
    db.init_app(app)

    # Global error handler
    @app.errorhandler(Exception)
    def handle_error(e):
        app.logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        # Never expose error details to client in any environment
        return {"error": "Internal server error"}, 500

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.request_routes import request_bp
    from routes.user_routes import user_bp
    from routes.config_routes import config_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(config_bp, url_prefix='/api')

    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    # Health check endpoint
    @app.route('/health')
    def health():
        return {"status": "healthy", "app": "TimeOff Manager"}, 200

    # Security headers middleware
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses"""
        # HTTPS enforcement in production
        if os.getenv('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'

        # Prevent MIME-type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # XSS Protection (legacy browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "cdn.tailwindcss.com unpkg.com cdn.jsdelivr.net "
            "fonts.googleapis.com fonts.gstatic.com"
        )

        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
