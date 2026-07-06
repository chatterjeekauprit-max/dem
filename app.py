import os
import uuid
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
VALERIX_CLOUD_BACKEND = "https://core-api.valerix-enterprise.com/v2/control"

@app.route("/")
def dashboard_home():
    return render_template("index.html")

@app.route("/api/v1/dispatch", methods=["POST"])
def dispatch_state_signal():
    payload = request.get_json()
    state_code = payload.get("state_code")
    license_key = payload.get("license_key")
    hardware_dna = payload.get("hardware_dna")

    handshake_packet = {
        "session_vector": str(uuid.uuid4())[:8],
        "target_operational_state": state_code,
        "token_signature": license_key,
        "telemetry_data": {
            "puf_fingerprint": hardware_dna,
            "peripheral_mac_mask": "00:1A:2B:3C:4D:5E",
            "liveness_stream_frame": "Verified_Liveness_True"
        }
    }
    try:
        cloud_response = requests.post(f"{VALERIX_CLOUD_BACKEND}/execute", json=handshake_packet, timeout=5)
        return jsonify(cloud_response.json())
    except requests.exceptions.RequestException:
        return jsonify({
            "status": "QUARANTINE_LOCKDOWN",
            "code": 403,
            "message": "Security Handshake Dropped. Valid Valerix Subscription Key Required."
        }), 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
