from src.server_management.server_manager import ServerManager
import os
from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from src.api import auth
from src.models.auth import Auth
from src.database import connector
import secrets

load_dotenv()
db = connector.DBConnector()
authen = Auth(db)

def create_app():
    app = Flask(__name__)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.secret_key = secrets.token_hex(32)
    
    # Initialize session
    Session(app)

    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')

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