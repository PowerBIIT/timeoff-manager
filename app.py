"""Flask application entry point"""
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_talisman import Talisman
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

    # HTTPS enforcement with Talisman (production only)
    if os.getenv('FLASK_ENV') == 'production':
        csp = {
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", "cdn.tailwindcss.com", "unpkg.com", "cdn.jsdelivr.net"],
            'style-src': ["'self'", "'unsafe-inline'", "cdn.tailwindcss.com", "fonts.googleapis.com"],
            'font-src': ["'self'", "fonts.gstatic.com"],
            'img-src': ["'self'", "data:"],
            'connect-src': ["'self'"]
        }
        Talisman(app,
                 force_https=True,
                 strict_transport_security=True,
                 strict_transport_security_max_age=31536000,
                 content_security_policy=csp,
                 content_security_policy_nonce_in=['script-src'],
                 feature_policy={'geolocation': "'none'", 'microphone': "'none'", 'camera': "'none'"})

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
    from routes.init_routes import init_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(request_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(config_bp, url_prefix='/api')
    app.register_blueprint(init_bp, url_prefix='/api')

    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    # Health check endpoint
    @app.route('/health')
    def health():
        return {"status": "healthy", "app": "TimeOff Manager"}, 200

    # Version endpoint
    @app.route('/api/version')
    def version():
        """Return git commit hash and deployment info"""
        try:
            import json
            import os

            # Try multiple paths
            paths = [
                'version.json',
                os.path.join(os.path.dirname(__file__), 'version.json'),
                '/home/site/wwwroot/version.json'
            ]

            version_info = None
            for path in paths:
                try:
                    with open(path, 'r') as f:
                        version_info = json.load(f)
                        break
                except (FileNotFoundError, IOError):
                    continue

            if version_info:
                return version_info, 200
            else:
                return {"commit": "unknown", "date": "unknown", "branch": "unknown", "error": "version.json not found"}, 200

        except Exception as e:
            app.logger.error(f"Version endpoint error: {str(e)}")
            return {"commit": "unknown", "date": "unknown", "branch": "unknown", "error": str(e)}, 200

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

        # Content Security Policy (IMPROVED - removed unsafe-eval)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.tailwindcss.com unpkg.com cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.tailwindcss.com fonts.googleapis.com; "
            "font-src 'self' fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )

        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions Policy (formerly Feature-Policy)
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
