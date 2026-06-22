import requests
import random
from flask import Flask, jsonify, request

app = Flask(__name__)

JAVA_BACKEND_URL = "http://localhost:8080/api/parking"


def generate_plate():
    cities = ["30A", "29B", "51F", "43A", "88K", "77B"]
    city = random.choice(cities)
    number = random.randint(1, 99999)

    return f"{city}{number:05d}"


def call_backend_get(endpoint, params):
    url = f"{JAVA_BACKEND_URL}{endpoint}"

    try:
        response = requests.get(url, params=params, timeout=5)

        try:
            data = response.json()
        except Exception:
            data = {
                "success": False,
                "message": "Backend không trả về JSON",
                "raw": response.text,
                "data": None
            }

        # Chống trường hợp backend trả null
        if data is None:
            data = {
                "success": False,
                "message": "Backend trả về null",
                "data": None
            }

        # Chống trường hợp backend trả list/string thay vì object
        if not isinstance(data, dict):
            data = {
                "success": False,
                "message": "Backend trả về dữ liệu không đúng dạng object",
                "raw": data,
                "data": None
            }

        print("JAVA STATUS:", response.status_code)
        print("JAVA RESPONSE:", data)

        return response.status_code, data

    except requests.exceptions.RequestException as e:
        return 500, {
            "success": False,
            "message": str(e),
            "data": None
        }


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Camera AI Simulator is running",
        "endpoints": {
            "checkin_random": "/auto-checkin",
            "checkin_plate": "/auto-checkin?plate=30A12345",
            "checkout_plate": "/auto-checkout?plate=30A12345",
            "auto_test": "/auto-test?plate=30A12345"
        }
    })


# =========================
# CAMERA CỔNG VÀO - CHECK-IN
# =========================
@app.route("/auto-checkin", methods=["GET"])
def auto_checkin():
    plate = request.args.get("plate")

    if not plate:
        plate = generate_plate()

    plate = plate.strip().upper().replace(" ", "")

    print(f"📷 CAMERA CỔNG VÀO: Phát hiện xe {plate}")

    status_code, data = call_backend_get(
        "/checkin",
        {
            "plate": plate
        }
    )

    backend_data = data.get("data") or {}

    if status_code == 200:
        return jsonify({
            "status": "Success" if data.get("success") else "Failed",
            "action": "CHECK_IN",
            "plate": plate,
            "assigned_slot": backend_data.get("slotId"),
            "backend_response": data
        }), 200

    return jsonify({
        "status": "Error",
        "action": "CHECK_IN",
        "plate": plate,
        "message": "Backend lỗi",
        "backend_response": data
    }), 500


# =========================
# CAMERA CỔNG RA - CHECK-OUT
# =========================
@app.route("/auto-checkout", methods=["GET"])
def auto_checkout():
    plate = request.args.get("plate")

    if not plate:
        return jsonify({
            "status": "Error",
            "message": "Thiếu biển số. Ví dụ: /auto-checkout?plate=30A12345"
        }), 400

    plate = plate.strip().upper().replace(" ", "")

    print(f"📷 CAMERA CỔNG RA: Phát hiện xe {plate}")

    status_code, data = call_backend_get(
        "/checkout/by-plate",
        {
            "plate": plate
        }
    )

    backend_data = data.get("data") or {}

    if status_code == 200:
        return jsonify({
            "status": "Success" if data.get("success") else "Failed",
            "action": "CHECK_OUT",
            "plate": plate,
            "slotId": backend_data.get("slotId"),
            "minutes": backend_data.get("minutes"),
            "amount": backend_data.get("amount"),
            "backend_response": data
        }), 200

    return jsonify({
        "status": "Error",
        "action": "CHECK_OUT",
        "plate": plate,
        "message": "Backend lỗi",
        "backend_response": data
    }), 500


# =========================
# GIỮ LẠI ENDPOINT CŨ
# =========================
@app.route("/auto-test", methods=["GET"])
def auto_test():
    return auto_checkin()


if __name__ == "__main__":
    print("📷 Camera AI Simulator chạy tại port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)