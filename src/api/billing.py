from flask import jsonify, request, Blueprint
from ..database.load_env import LoadDBEnv
from ..database.billing import Billing
from ..database.auth import Auth
from ..database import connector
from ..decorators import token_required

billing_bp = Blueprint("billing", __name__)
# not finished
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
    subscription_id = data.get("subscription_id")
    amount = data.get("amount")

    if not all([customer_id, subscription_id, amount]):
        db.close()
        return jsonify({"message": "Missing required data"}), 400
    
    billing.add_billing(customer_id, subscription_id, amount)
    db.close()
    return jsonify({"message": "Billing record added successfully"}), 200

@billing_bp.route("/delete_billing/<billing_id>", methods=["DELETE"])
@token_required
def delete_billing(billing_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)
    
    billing.delete_billing(billing_id)
    db.close()
    return jsonify({"message": "Billing record deleted successfully"}), 200

@billing_bp.route("/update_billing_status/<billing_id>", methods=["PUT"])
@token_required
def update_billing_status(billing_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    billing = Billing(db)
    
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

    username = request.jwt_payload.get("username")
   
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
