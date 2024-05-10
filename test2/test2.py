
import hmac
import hashlib

# # parameters send to MoMo get get payUrl
# endpoint = "https://payment.momo.vn/v2/gateway/api/create"
# partnerCode = "MOMOGA7H20210625"
# accessKey = "McUXWgJnL1oO7rts"
# secretKey = "WrMedUoTMhCzr99mblxKRUl4WykQgTqP"
# orderInfo = "pay with MoMo"
# redirectUrl = "https://master-help-desk-back-end.vercel.app"
# ipnUrl = "https://master-help-desk-back-end.vercel.app/billing/handle_transaction"
# amount = "10000"
# orderId = "lhehHWAt6eaU0LNXId8BEHC_xOguA839KSUvZR5Zc"
# requestId = "lhehHWAt6eaU0LNXId8BEHC_xOguA839KSUvZR5Zc"
# requestType = "captureWallet"
# extraData = ""  # pass empty value or Encode base64 JsonString

# rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType

# # puts raw signature
# print("--------------------RAW SIGNATURE----------------")
# print(rawSignature)
# # signature
# h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
# signature = h.hexdigest()
# print("--------------------SIGNATURE----------------")
# print(signature)
# parameters send to MoMo get get payUrl
endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
partnerCode = "MOMO"
accessKey = "F8BBA842ECF85"
secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
orderInfo = "pay with MoMo"
redirectUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
amount = "50000"
orderId = "lhehHWAt6eaU0LNXId8BEHC_xOguA839KSUvZR5Zc"
requestId = 'lhehHWAt6eaU0LNXId8BEHC_xOguA839KSUvZR5Zc'
requestType = "captureWallet"
extraData = ""  # pass empty value or Encode base64 JsonString

rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType

# puts raw signature
print("--------------------RAW SIGNATURE----------------")
print(rawSignature)
# signature
h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
signature = h.hexdigest()
print("--------------------SIGNATURE----------------")
print(signature)
