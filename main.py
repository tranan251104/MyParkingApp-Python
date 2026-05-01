import requests
import random
from flask import Flask, jsonify

app = Flask(__name__)

# Cấu hình kết nối tới Java Backend
# Lưu ý: Java chạy ở port 8080
JAVA_BACKEND_URL = "http://localhost:8080/api/parking"

TOTAL_SLOTS = 1000
occupied_slots = {}  # Lưu trữ tạm: { slotId: plate }


def generate_plate():
    cities = ["30A", "29B", "51F", "43A", "88K", "77B"]
    city = random.choice(cities)
    number = random.randint(00000, 99999)
    return f"{city}-{number}"


# API để kích hoạt xe vào (Check-in)
@app.route('/auto-test', methods=['GET'])
def simulate_check_in():
    plate = generate_plate()
    # Sinh ngẫu nhiên một ô đỗ từ S1 đến S1000
    slot_id = f"S{random.randint(1, TOTAL_SLOTS)}"

    if slot_id not in occupied_slots:
        print(f"📷 CAMERA: Phát hiện xe {plate} vào ô {slot_id}")

        # TỰ SINH LINK VÀ GỌI JAVA BACKEND
        url = f"{JAVA_BACKEND_URL}/checkin?slotId={slot_id}&plate={plate}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                occupied_slots[slot_id] = plate
                return jsonify({
                    "status": "Success",
                    "message": f"Đã báo cho Java: Xe {plate} vào ô {slot_id}",
                    "data": response.json()
                })
            else:
                return jsonify({"status": "Error", "message": "Java Backend tra ve loi"}), 500
        except Exception as e:
            return jsonify({"status": "Error", "message": str(e)}), 500

    return jsonify({"status": "Warning", "message": "O do da co xe, thu lai lan sau"})


if __name__ == '__main__':
    print("Camera AI Simulator đang chạy tại port 5000...")
    app.run(host='0.0.0.0', port=5000)