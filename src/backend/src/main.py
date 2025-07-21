import os
import sys
import asyncio
import logging
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.oracle_ai_simple import oracle_ai_bp
from src.routes.nlu import nlu_bp
from src.routes.transcript import transcript_bp
from src.routes.human_needs_dashboard import human_needs_dashboard_bp
from src.services.nlu_service import nlu_service
from src.services.conversation_service import conversation_service
from src.services.intent_service import intent_service
from src.services.transcript_service import transcript_service
from src.security.auth import auth_manager
from src.security.rate_limiting import rate_limiter

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Initialize security components
auth_manager.init_app(app)
rate_limiter.init_app(app)

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize NLU services
async def init_services():
    """Initialize NLU services"""
    try:
        await nlu_service.initialize()
        await conversation_service.initialize()
        await intent_service.initialize()
        await transcript_service.initialize()
        logging.info("NLU services initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize NLU services: {str(e)}")

# Run service initialization
asyncio.run(init_services())

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(oracle_ai_bp, url_prefix='/api/oracle')
app.register_blueprint(nlu_bp)
app.register_blueprint(transcript_bp)
app.register_blueprint(human_needs_dashboard_bp)

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
