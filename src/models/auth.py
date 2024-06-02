import base64
import hashlib
from datetime import datetime
import random
import string
import smtplib, ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Auth:
    def __init__(self) -> None:
        pass

    def generate_id(self, name: str) -> str:
        # Get current time
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")

        # Combine name and current time
        server_info = f"{name}/{current_time}"

        # Generate a hash digest using SHA-256
        hash_digest = hashlib.sha256(server_info.encode()).digest()

        # Encode hash digest to Base64 without padding and remove hyphens
        id = base64.urlsafe_b64encode(hash_digest).decode().rstrip('=').replace('-', '')

        return id

    def encrypt_password(self, password: str, user_id: str) -> str:
        # Combine user_id and password
        combined_string = f"{user_id}/{password}"

        # Hash the combined string using SHA-256
        hashed_password = hashlib.sha256(combined_string.encode()).digest()

        # Base64 encode the hashed password
        encoded_password = base64.b64encode(hashed_password)

        return encoded_password.decode()

    def compare_passwords(self, user_id, entered_password, stored_password):
        # Hash the entered password using the same method as the stored password
        hashed_entered_password = self.encrypt_password(entered_password, user_id)

        # Compare the hashed entered password with the stored password
        return hashed_entered_password == stored_password

    # Simple OTP generation function
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))

    # Email sending function
    def send_email(self, email, otp):
        sender_email = os.environ.get("OTP_EMAIL")
        receiver_email = email
        password = os.environ.get("OTP_EMAIL_PASS")

        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "[MHD] This is your OTP Email"

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
        """.replace("%s", otp)

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

    

