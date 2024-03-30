from dotenv import load_dotenv
from flask import Flask
from src.api.auth import auth_bp
from src.api.organization import organization_bp
from src.api.manager import manager_bp
import secrets
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SESSION_TYPE"] = "filesystem"
    app.secret_key = secrets.token_hex(32)  

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(organization_bp, url_prefix="/org")
    app.register_blueprint(manager_bp, url_prefix="/manager")

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