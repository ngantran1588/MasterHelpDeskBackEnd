from datetime import datetime, timezone
import json
import requests
import os
import hmac
import hashlib
import base64
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import connector
from ..const import const
from ..models.billing import Billing
from ..models.auth import Auth as AuthAPI

class Billing:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.auth = AuthAPI()

    def add_billing(self, customer_id: str, amount: float) -> None:
        try:
            billing_id = self.auth.generate_id(customer_id)
            timestamp = datetime.now(timezone.utc)
            billing_status = const.BILLING_STATUS_PENDING
            subscription_id = const.NULL_VALUE

            secret_key = os.environ.get("SECRET_KEY")
            access_key = os.environ.get("MOMO_ACCESS_KEY")
            ipn_url = os.environ.get("IPN_URL")
            redirect_url = os.environ.get("REDIRECT_URL")
            partner_code = os.environ.get("MOMO_PARTNER_CODE")
            endpoint = os.environ.get("MOMO_ENDPOINT")

            extra_data = {"customer_id": customer_id}
            extra_data_encode = base64.b64encode(str(extra_data).encode('utf-8'))
            extra_data_encode = str(extra_data_encode).replace("b'","").replace("'", "")
            data = {
                "accessKey": access_key,
                "amount": amount,
                "extraData": extra_data_encode,
                "ipnUrl": ipn_url,
                "orderId": billing_id,
                "orderInfo": "Master Help Desk",
                "partnerCode": partner_code,
                "redirectUrl": redirect_url,
                "requestId": billing_id,
                "requestType": "captureWallet"
            }

            signature = self.create_signature(secret_key, data)
            return_data = {
                "partnerCode": partner_code,
                "requestType": "captureWallet",
                "ipnUrl": ipn_url,
                "redirectUrl": redirect_url,
                "orderId": billing_id,
                "amount": amount,
                "lang": "en",
                "orderInfo": "Master Help Desk",
                "requestId": billing_id,
                "extraData": extra_data_encode,
                "signature": signature
            }

            query = """INSERT INTO tbl_billing (billing_id, customer_id, subscription_id, timestamp, billing_status, amount, signature) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (billing_id, customer_id, subscription_id, timestamp, billing_status, amount, signature)
            self.db.execute_query(query, values)
            print("Billing record added successfully.")

            data = json.dumps(return_data)

            clen = len(data)
            response = requests.post(endpoint, data=data, headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

            response_json = response.json()
            if response_json["resultCode"] != 0:
                return None
            
            return response_json["payUrl"]
        except Exception as e:
            print("Error adding billing record:", e)
            return None

    def create_signature(self, secret_key: str, data: dict):
        # Sort the data dictionary by keys and concatenate key-value pairs
        sorted_values = "&".join([f"{key}={data[key]}" for key in sorted(data.keys())])
        
        # Create the HMAC-SHA256 signature using the secret key and sorted values
        h = hmac.new(bytes(secret_key, "ascii"), bytes(sorted_values, "ascii"), hashlib.sha256)
        signature = h.hexdigest()

        return signature
    
    def check_signature(self, billing_id: str, signature: str):
        try:
            query = """SELECT signature FROM tbl_billing WHERE billing_id = %s"""
            values = (billing_id,)
            signature_db = self.db.execute_query(query, values)[0][0]
            if signature == signature_db:
                return True
            return False
            
        except Exception as e:
            return False

    def delete_billing(self, billing_id: str) -> None:
        try:
            query = """DELETE FROM tbl_billing WHERE billing_id = %s"""
            values = (billing_id,)
            self.db.execute_query(query, values)
            print("Billing record deleted successfully.")
        except Exception as e:
            print("Error deleting billing record:", e)

    def update_billing_status(self, billing_id: str, new_status: str) -> None:
        try:
            query = """UPDATE tbl_billing SET billing_status = %s WHERE billing_id = %s"""
            values = (new_status, billing_id)
            self.db.execute_query(query, values)
            print("Billing status updated successfully.")
        except Exception as e:
            print("Error updating billing status:", e)
    
    def update_success_transaction(self, billing_id: str, new_status: str, subscription_id: str) -> None:
        try:
            query = """UPDATE tbl_billing SET billing_status = %s, subscription_id = %s WHERE billing_id = %s"""
            values = (new_status, subscription_id, billing_id)
            self.db.execute_query(query, values)
            print("Billing status updated successfully.")
        except Exception as e:
            print("Error updating billing:", e)

    def get_billing_by_id(self, billing_id: str):
        try:
            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing WHERE billing_id = %s"""
            values = (billing_id,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None
            
            billing_info = result[0]
            billing = {
                "billing_id": billing_info[0],
                "customer_id": billing_info[1],
                "subscription_id": billing_info[2],
                "timestamp": billing_info[3],
                "billing_status": billing_info[4],
                "amount": billing_info[5],
            }

            return billing
        except Exception as e:
            print("Error fetching billing record:", e)
            return None

    def get_all_billing(self):
        try:
            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing"""
            result = self.db.execute_query(query)

            if len(result) == 0:
                return None
            billings = []
            for billing_info in result:
                # Extract billings information and create a dictionary
                billing = {
                    "billing_id": billing_info[0],
                    "customer_id": billing_info[1],
                    "subscription_id": billing_info[2],
                    "timestamp": billing_info[3],
                    "billing_status": billing_info[4],
                    "amount": billing_info[5],
                }
                billings.append(billing)

            return billings
        except Exception as e:
            print("Error fetching all billing records:", e)
            return None

    def get_billing_by_customer_id(self, username: str):
        try:
            query_username = """SELECT customer_id FROM tbl_customer WHERE username = %s"""
            value = (username,)
            customer_id = self.db.execute_query(query_username, value)[0][0]

            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing WHERE customer_id = %s"""
            values = (customer_id,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None
            billings = []
            for billing_info in result:
                # Extract billings information and create a dictionary
                billing = {
                    "billing_id": billing_info[0],
                    "customer_id": billing_info[1],
                    "subscription_id": billing_info[2],
                    "timestamp": billing_info[3],
                    "billing_status": billing_info[4],
                    "amount": billing_info[5],
                }
                billings.append(billing)

            return billings
        except Exception as e:
            print("Error fetching billing records by customer ID:", e)
            return None

    def get_billing_by_status(self, status: str):
        try:
            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing WHERE billing_status = %s"""
            values = (status,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None
            billings = []
            for billing_info in result:
                # Extract billings information and create a dictionary
                billing = {
                    "billing_id": billing_info[0],
                    "customer_id": billing_info[1],
                    "subscription_id": billing_info[2],
                    "timestamp": billing_info[3],
                    "billing_status": billing_info[4],
                    "amount": billing_info[5],
                }
                billings.append(billing)

            return billings
        except Exception as e:
            print("Error fetching billing records by status:", e)
            return None
    
    def get_billing_status_by_customer_id(self, status: str, customer_id: str):
        try:
            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing WHERE billing_status = %s AND customer_id = %s"""
            values = (status, customer_id,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None
            billings = []
            for billing_info in result:
                # Extract billings information and create a dictionary
                billing = {
                    "billing_id": billing_info[0],
                    "customer_id": billing_info[1],
                    "subscription_id": billing_info[2],
                    "timestamp": billing_info[3],
                    "billing_status": billing_info[4],
                    "amount": billing_info[5],
                }
                billings.append(billing)

            return billings
        except Exception as e:
            print("Error fetching billing records by status:", e)
            return None
        
    # Email sending function
    def send_email(self, email, billing: Billing):
        sender_email = os.environ.get("OTP_EMAIL")
        receiver_email = email
        password = os.environ.get("OTP_EMAIL_PASS")

        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "[MHD] Transaction Successful"

        text = """
                    <!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">

            <head>
            <!--[if gte mso 9]>
            <xml>
            <o:OfficeDocumentSettings>
                <o:AllowPNG/>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
            </xml>
            <![endif]-->
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="x-apple-disable-message-reformatting">
            <!--[if !mso]><!-->
            <meta http-equiv="X-UA-Compatible" content="IE=edge"><!--<![endif]-->
            <title></title>

            <style type="text/css">
                @media only screen and (min-width: 520px) {
                .u-row {
                    width: 500px !important;
                }

                .u-row .u-col {
                    vertical-align: top;
                }

                .u-row .u-col-100 {
                    width: 500px !important;
                }

                }

                @media (max-width: 520px) {
                .u-row-container {
                    max-width: 100% !important;
                    padding-left: 0px !important;
                    padding-right: 0px !important;
                }

                .u-row .u-col {
                    min-width: 320px !important;
                    max-width: 100% !important;
                    display: block !important;
                }

                .u-row {
                    width: 100% !important;
                }

                .u-col {
                    width: 100% !important;
                }

                .u-col>div {
                    margin: 0 auto;
                }
                }

                body {
                margin: 0;
                padding: 0;
                }

                table,
                tr,
                td {
                vertical-align: top;
                border-collapse: collapse;
                }

                p {
                margin: 0;
                }

                .ie-container table,
                .mso-container table {
                table-layout: fixed;
                }

                * {
                line-height: inherit;
                }

                a[x-apple-data-detectors='true'] {
                color: inherit !important;
                text-decoration: none !important;
                }

                table,
                td {
                color: #000000;
                }
            </style>



            </head>

            <body class="clean-body u_body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #f3f8ff;color: #000000">
            <!--[if IE]><div class="ie-container"><![endif]-->
            <!--[if mso]><div class="mso-container"><![endif]-->
            <table style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #f3f8ff;width:100%" cellpadding="0" cellspacing="0">
                <tbody>
                <tr style="vertical-align: top">
                    <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color: #f3f8ff;"><![endif]-->



                    <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:500px;"><tr style="background-color: transparent;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="500" style="background-color: #3867a5;width: 500px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 500px;display: table-cell;vertical-align: top;">
                            <div style="background-color: #3867a5;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                <!--[if (!mso)&(!IE)]><!-->
                                <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:arial,helvetica,sans-serif;" align="left">

                                        <table height="0px" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 0px solid ;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
                                            <tbody>
                                            <tr style="vertical-align: top">
                                                <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;font-size: 0px;line-height: 0px;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
                                                <span>&#160;</span>
                                                </td>
                                            </tr>
                                            </tbody>
                                        </table>

                                        </td>
                                    </tr>
                                    </tbody>
                                </table>

                                <!--[if (!mso)&(!IE)]><!-->
                                </div><!--<![endif]-->
                            </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                        </div>
                        </div>
                    </div>

                    <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:500px;"><tr style="background-color: transparent;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="500" style="width: 500px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 500px;display: table-cell;vertical-align: top;">
                            <div style="height: 100%;width: 100% !important;">
                                <!--[if (!mso)&(!IE)]><!-->
                                <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->

                                <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="overflow-wrap:break-word;word-break:break-word;padding:0px;font-family:arial,helvetica,sans-serif;" align="left">

                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                            <td style="padding-right: 0px;padding-left: 0px;" align="center">

                                                <img align="center" border="0" src="https://assets.unlayer.com/projects/224259/1711280043328-MHDLogo.png" alt="" title="" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 19%;max-width: 95px;" width="95" />

                                            </td>
                                            </tr>
                                        </table>

                                        </td>
                                    </tr>
                                    </tbody>
                                </table>

                                <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:arial,helvetica,sans-serif;" align="left">

                                        <!--[if mso]><table width="100%"><tr><td><![endif]-->
                                        <h1 style="margin: 0px; color: #3867a5; line-height: 140%; text-align: center; word-wrap: break-word; font-family: inherit; font-size: 22px; font-weight: 400;"><span><span><span><span><span><span><strong>MASTER HELP DESK</strong></span></span></span></span></span></span></h1>
                                        <!--[if mso]></td></tr></table><![endif]-->

                                        </td>
                                    </tr>
                                    </tbody>
                                </table>

                                <!--[if (!mso)&(!IE)]><!-->
                                </div><!--<![endif]-->
                            </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                        </div>
                        </div>
                    </div>

                    <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:500px;"><tr style="background-color: transparent;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="500" style="width: 500px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 500px;display: table-cell;vertical-align: top;">
                            <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                <!--[if (!mso)&(!IE)]><!-->
                                <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:arial,helvetica,sans-serif;" align="left">

                                        <table height="0px" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 1px solid #BBBBBB;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
                                            <tbody>
                                            <tr style="vertical-align: top">
                                                <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;font-size: 0px;line-height: 0px;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
                                                <span>&#160;</span>
                                                </td>
                                            </tr>
                                            </tbody>
                                        </table>

                                        </td>
                                    </tr>
                                    </tbody>
                                </table>

                                <!--[if (!mso)&(!IE)]><!-->
                                </div><!--<![endif]-->
                            </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                        </div>
                        </div>
                    </div>

                    <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #ffffff;">
                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:500px;"><tr style="background-color: #ffffff;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="500" style="width: 500px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 500px;display: table-cell;vertical-align: top;">
                            <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                <!--[if (!mso)&(!IE)]><!-->
                                <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="overflow-wrap:break-word;word-break:break-word;padding:20px;font-family:arial,helvetica,sans-serif;" align="left">

                                        <div style="font-size: 14px; line-height: 140%; text-align: left; word-wrap: break-word;">
                                            <p style="list-style-type: disc; line-height: 140%;">Hello,</p>
                                            <p style="list-style-type: disc; line-height: 140%;">&nbsp;</p>
                                            <p style="list-style-type: disc; line-height: 140%;">Here is a temporary security&nbsp;code&nbsp;for your Master Help Desk Account. It can only be used once within the next <strong>5</strong>&nbsp;minutes, after which it will expire:</p>
                                        </div>

                                        </td>
                                    </tr>
                                    </tbody>
                                </table>

                                <!--[if (!mso)&(!IE)]><!-->
                                </div><!--<![endif]-->
                            </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                        </div>
                        </div>
                    </div>

                    <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:500px;"><tr style="background-color: transparent;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="500" style="background-color: #3867a5;width: 500px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 500px;display: table-cell;vertical-align: top;">
                            <div style="background-color: #3867a5;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                <!--[if (!mso)&(!IE)]><!-->
                                <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="overflow-wrap:break-word;word-break:break-word;padding:20px;font-family:arial,helvetica,sans-serif;" align="left">

                                        <div style="font-size: 32px; color: #fffdfd; line-height: 140%; text-align: center; word-wrap: break-word;">
                                            <p style="line-height: 140%;"><strong>%s</strong></p>
                                        </div>

                                        </td>
                                    </tr>
                                    </tbody>
                                </table>

                                <!--[if (!mso)&(!IE)]><!-->
                                </div><!--<![endif]-->
                            </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                        </div>
                        </div>
                    </div>

                    <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #ffffff;">
                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:500px;"><tr style="background-color: #ffffff;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="500" style="width: 500px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 500px;display: table-cell;vertical-align: top;">
                            <div style="height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                <!--[if (!mso)&(!IE)]><!-->
                                <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="overflow-wrap:break-word;word-break:break-word;padding:20px;font-family:arial,helvetica,sans-serif;" align="left">

                                        <div style="font-size: 14px; line-height: 140%; text-align: left; word-wrap: break-word;">
                                            <p style="list-style-type: disc; line-height: 140%;">Did you receive this email without having an active request from Master Help Desk to enter a verification&nbsp;code? If so, the security of your Master Help Desk account may be compromised. Please change your password as soon as possible.</p>
                                            <p style="list-style-type: disc; line-height: 140%;">&nbsp;</p>
                                            <p style="list-style-type: disc; line-height: 140%;">Sincerely,</p>
                                            <p style="list-style-type: disc; line-height: 140%;">Master Help Desk Team</p>
                                        </div>

                                        </td>
                                    </tr>
                                    </tbody>
                                </table>

                                <!--[if (!mso)&(!IE)]><!-->
                                </div><!--<![endif]-->
                            </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                        </div>
                        </div>
                    </div>

                    <div class="u-row-container" style="padding: 0px;background-color: transparent">
                        <div class="u-row" style="margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;">
                        <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:500px;"><tr style="background-color: transparent;"><![endif]-->

                            <!--[if (mso)|(IE)]><td align="center" width="500" style="background-color: #3867a5;width: 500px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;" valign="top"><![endif]-->
                            <div class="u-col u-col-100" style="max-width: 320px;min-width: 500px;display: table-cell;vertical-align: top;">
                            <div style="background-color: #3867a5;height: 100%;width: 100% !important;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;">
                                <!--[if (!mso)&(!IE)]><!-->
                                <div style="box-sizing: border-box; height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;border-radius: 0px;-webkit-border-radius: 0px; -moz-border-radius: 0px;"><!--<![endif]-->

                                <table style="font-family:arial,helvetica,sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:arial,helvetica,sans-serif;" align="left">

                                        <table height="0px" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;border-top: 0px solid #BBBBBB;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
                                            <tbody>
                                            <tr style="vertical-align: top">
                                                <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top;font-size: 0px;line-height: 0px;mso-line-height-rule: exactly;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%">
                                                <span>&#160;</span>
                                                </td>
                                            </tr>
                                            </tbody>
                                        </table>

                                        </td>
                                    </tr>
                                    </tbody>
                                </table>

                                <!--[if (!mso)&(!IE)]><!-->
                                </div><!--<![endif]-->
                            </div>
                            </div>
                            <!--[if (mso)|(IE)]></td><![endif]-->
                            <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                        </div>
                        </div>
                    </div>

                    <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                    </td>
                </tr>
                </tbody>
            </table>
            <!--[if mso]></div><![endif]-->
            <!--[if IE]></div><![endif]-->
            </body>

            </html>
        """.replace("%s", billing)

        message.attach(MIMEText(text, "html"))
        gmail_host = os.environ.get("GMAIL_HOST")
        gmail_port = os.environ.get("GMAIL_PORT")
        context = ssl.create_default_context()
        with smtplib.SMTP(gmail_host, gmail_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
   