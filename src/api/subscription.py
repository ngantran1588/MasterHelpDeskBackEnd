from flask import jsonify, request, Blueprint
from datetime import datetime
from ..database.load_env import LoadDBEnv
from ..database.subscription import Subscription
from ..database.auth import Auth
from ..database.organization import Organization
from ..database import connector
from ..const import const
from ..decorators import token_required

subscription_bp = Blueprint("subscription", __name__)
@subscription_bp.route("/check_subscription_by_username", methods=["GET"])
@token_required
def check_subscription_by_username():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    sub = Subscription(db)
    
    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    sub_data = sub.check_subscription_by_username(username)
    db.close()

    if sub_data:
        return jsonify({"message": "Subcription bought !"}), 200
    else:
        return jsonify({"message": "Subcription not found"}), 500

@subscription_bp.route("/update_subscription_status/<subscription_id>", methods=["POST"])
@token_required
def update_subscription_status(subscription_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    sub = Subscription(db)
    auth = Auth(db)
    org = Organization(db)

    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    data = request.get_json()
    new_status = data.get("new_status")
    
    if new_status == const.STATUS_INACTIVE:
        auth.change_role_to_user(username)
        organization_id = org.get_organization_id_by_sub(subscription_id)
        if not organization_id:
            sub.update_subscription_status(subscription_id, new_status)
            db.close()
            return jsonify({"message": "Subscription status updated successfully."}), 200
        result = org.change_organization_status(organization_id, const.STATUS_INACTIVE)
        if not result:
            db.close()
            return jsonify({"message": "Error in querying database."}), 500
        
    sub.update_subscription_status(subscription_id, new_status)
    db.close()

    return jsonify({"message": "Subscription status updated successfully."}), 200

@subscription_bp.route("/check_expiration", methods=["GET"])
@token_required
def check_expiration():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    sub = Subscription(db)
    org = Organization(db)
    auth = Auth(db)

    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    customer_id = auth.get_customer_id_from_username(username) 

    subscription_info = sub.get_subscriptions_by_customer_id(customer_id)

    if not subscription_info:
        db.close()
        return jsonify({"message": "Did not buy subcription", "status": False}), 200

    subscription_id = subscription_info[0]["subscription_id"]
    subscription = sub.get_subscription_by_id(subscription_id)

    if subscription:
        expiration_date = datetime.fromisoformat(subscription["expiration_date"])
        expiration_msg, status = sub.check_expiration(expiration_date)
        if status:
            auth.change_role_to_user(username)
            organization_id = org.get_organization_id_by_sub(subscription_id)
            if not organization_id:
                db.close()
                return jsonify({"message": "Error in querying database."}), 500
            result = org.change_organization_status(organization_id, const.STATUS_INACTIVE)
            if not result:
                db.close()
                return jsonify({"message": "Error in querying database."}), 500
        db.close()
        return jsonify({"message": expiration_msg, "status": status}), 200
    else:
        db.close()
        return jsonify({"message": "Subscription not found."}), 404

@subscription_bp.route("/check_expiration_by_id/<subscription_id>", methods=["GET"])
@token_required
def check_expiration_by_id(subscription_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    sub = Subscription(db)

    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    subscription = sub.get_subscription_by_id(subscription_id)
    db.close()

    if subscription:
        expiration_date = datetime.fromisoformat(subscription["expiration_date"])
        expiration_msg, status = sub.check_expiration(expiration_date)
        return jsonify({"message": expiration_msg, "status": status}), 200
    else:
        return jsonify({"message": "Subscription not found."}), 404

@subscription_bp.route("/get_subscription_by_id/<subscription_id>", methods=["GET"])
@token_required
def get_subscription_by_id(subscription_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    sub = Subscription(db)

    username = request.jwt_payload.get("manager_username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    subscription = sub.get_subscription_by_id(subscription_id)
    db.close()

    if subscription:
        return jsonify(subscription), 200
    else:
        return jsonify({"message": "Subscription not found."}), 404

@subscription_bp.route("/get_all_subscriptions", methods=["GET"])
@token_required
def get_all_subscriptions():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    sub = Subscription(db)

    username = request.jwt_payload.get("manager_username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    subscriptions = sub.get_all_subscriptions()
    db.close()

    if subscriptions:
        return jsonify(subscriptions), 200
    else:
        return jsonify({"message": "No subscriptions found."}), 404

@subscription_bp.route("/get_subscriptions_by_customer_id", methods=["GET"])
@token_required
def get_subscriptions_by_customer_id():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    sub = Subscription(db)
    auth = Auth(db)

    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    customer_id = auth.get_customer_id_from_username(username)

    subscriptions = sub.get_subscriptions_by_customer_id(customer_id)
    db.close()

    if subscriptions:
        return jsonify(subscriptions), 200
    else:
        return jsonify({"message": "No subscriptions found for the specified customer ID"}), 404
    
    