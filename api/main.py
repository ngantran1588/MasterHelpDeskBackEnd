from flask import Flask
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.api.auth import auth_bp
from src.api.organization import organization_bp
from src.api.manager import manager_bp
from src.api.package import package_bp
from src.api.server import server_bp
from src.api.guide import guide_bp
from src.api.role import role_bp
from src.api.subscription import subscription_bp
from src.api.billing import billing_bp
import secrets
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_SECURE_COOKIE"] = True
app.secret_key = secrets.token_hex(32)  

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(organization_bp, url_prefix="/org")
app.register_blueprint(manager_bp, url_prefix="/manager")
app.register_blueprint(package_bp, url_prefix="/package")
app.register_blueprint(server_bp, url_prefix="/server")
app.register_blueprint(guide_bp, url_prefix="/guide")
app.register_blueprint(role_bp, url_prefix="/role")
app.register_blueprint(subscription_bp, url_prefix="/subscription")
app.register_blueprint(billing_bp, url_prefix="/billing")

if __name__ == "__main__":
    app.run()