from flask import jsonify, request, Blueprint
from datetime import datetime, timezone, timedelta
import base64
from ..database.load_env import LoadDBEnv
from ..database.billing import Billing
from ..database.auth import Auth
from ..database.package import Package
from ..database.subscription import Subscription
from ..database import connector
from ..const import const
from ..decorators import token_required

billing_bp = Blueprint("billing", __name__)

@billing_bp.route("/add_billing", methods=["POST"])
@token_required
def add_billing():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    
    billing = Billing(db)
    auth = Auth(db)
    
    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    customer_id = auth.get_customer_id_from_username(username)
    amount = data.get("amount")

    if not all([customer_id, amount]):
        db.close()
        return jsonify({"message": "Missing required data"}), 400
    
    pay_url = billing.add_billing(customer_id, amount)

    db.close()

    if pay_url == None:
        return jsonify({"message": "Error connecting to momo"}), 500

    return jsonify({"message": "Billing record added successfully", "pay_url": pay_url}), 200

@billing_bp.route("/handle_transaction", methods=["POST"])
def handle_transaction():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)
    subscription = Subscription(db)
    package = Package(db)

    data = request.get_json()

    billing_id = data.get("orderId")
    result_code = data.get("resultCode")
    signature = data.get("signature")
    amount = data.get("amount")
    extra_data = data.get("extraData")

    extra_data = base64.b64decode(extra_data).decode('utf-8')
    extra_data = eval(extra_data)

    package_info = package.get_package_by_amount(amount)
    subscription_name = "{} for {} days".format(package_info["package_name"], package_info["duration"])
    expiration_time = datetime.now(timezone.utc) + timedelta(days=int(package_info["duration"]))
    if billing.check_signature(billing_id, signature):
        if result_code == 0:
            subscription_id = subscription.add_subscription(subscription_name, extra_data["customer_id"], package_info["package_id"], expiration_time, False)
            if subscription_id != None:
                billing.update_success_transaction(billing_id, const.BILLING_STATUS_SUCCESS, subscription_id)
    return 204


@billing_bp.route("/delete_billing/<billing_id>", methods=["DELETE"])
@token_required
def delete_billing(billing_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)

    username = request.jwt_payload.get("manager_username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    billing.delete_billing(billing_id)
    db.close()
    return jsonify({"message": "Billing record deleted successfully"}), 200

@billing_bp.route("/update_billing_status/<billing_id>", methods=["PUT"])
@token_required
def update_billing_status(billing_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)

    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    new_status = data.get("new_status")

    if not new_status:
        db.close()
        return jsonify({"message": "New status is missing"}), 400
    
    billing.update_billing_status(billing_id, new_status)
    db.close()
    return jsonify({"message": "Billing status updated successfully"}), 200

@billing_bp.route("/get_billing_by_id/<billing_id>", methods=["GET"])
@token_required
def get_billing_by_id(billing_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)

    username = request.jwt_payload.get("manager_username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    billing_info = billing.get_billing_by_id(billing_id)
    db.close()
    
    if billing_info:
        return jsonify(billing_info), 200
    else:
        return jsonify({"message": "Billing record not found"}), 404

@billing_bp.route("/get_all_billing", methods=["GET"])
@token_required
def get_all_billing():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)

    username = request.jwt_payload.get("manager_username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    
    all_billing = billing.get_all_billing()
    db.close()
    
    if all_billing:
        return jsonify(all_billing), 200
    else:
        return jsonify({"message": "No billing records found"}), 404
    
@billing_bp.route("/get_billing_by_status", methods=["GET"])
@token_required
def get_billing_by_status():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)

    username = request.jwt_payload.get("manager_username")
   
    if username == None:
        return jsonify({"message": "Permission denied"}), 403

    data = request.get_json()
    status = data.get(status)
    if not status:
        return jsonify({"message": "Status not found"}), 500
    
    billing_info = billing.get_billing_by_status(status)
    db.close()
    
    if billing_info:
        return jsonify(billing_info), 200
    else:
        return jsonify({"message": "Billing record not found"}), 404

@billing_bp.route("/get_billing_status_by_customer_id", methods=["GET"])
@token_required
def get_billing_status_by_customer_id():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)
    auth = Auth(db)

    username = request.jwt_payload.get("username")
   
    if username == None:
        return jsonify({"message": "Permission denied"}), 403

    data = request.get_json()
    status = data.get(status)
    if not status:
        return jsonify({"message": "Status not found"}), 500
    customer_id = auth.get_customer_id_from_username(username)
    billing_info = billing.get_billing_status_by_customer_id(status, customer_id)
    db.close()
    
    if billing_info:
        return jsonify(billing_info), 200
    else:
        return jsonify({"message": "Billing record not found"}), 404