# from dotenv import load_dotenv
# from flask import Flask
# from src.api.auth import auth_bp
# from src.api.organization import organization_bp
# from src.api.manager import manager_bp
# from src.api.package import package_bp
# import secrets
# from flask_cors import CORS
from flask import Flask
from src.api.auth import auth_bp
from src.api.organization import organization_bp
from src.api.manager import manager_bp
from src.api.package import package_bp
from src.api.server import server_bp
import secrets
from flask_cors import CORS

def create_app():
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

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()

    # # Replace these with your server details
    # server_hostname = os.environ.get("SERVER_HOSTNAME")
    # server_username = os.environ.get("SERVER_USERNAME")
    # private_key_path = os.environ.get("PRIVATE_KEY_PATH")
    # script_path = os.environ.get("SCRIPT_PATH")

    # # Initialize the ServerManager with private key authentication
    # server_manager = ServerManager(server_hostname, server_username, private_key_path=private_key_path)

    # # Connect to the server
    # server_manager.connect()

    # server_manager.upload_file_to_remote("src/scripts/execute_code/execute_code.sh", "/root/julia")

    # # Disconnect from the server
    # server_manager.disconnect()