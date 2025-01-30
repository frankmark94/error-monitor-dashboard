import requests
import json
from datetime import datetime
import time
import random

def send_test_error():
    url = "http://localhost:5000/endpoint"
    
    # Sample error types
    error_types = [
        (500, "Internal Server Error"),
        (404, "Resource Not Found"),
        (403, "Authentication Failed"),
        (502, "Gateway Error"),
        (400, "Invalid Request")
    ]
    
    # Sample connection types
    connection_types = ["SMS", "Email", "WhatsApp", "Voice", "Chat"]
    
    # Generate random error
    error_code, error_message = random.choice(error_types)
    
    payload = {
        "ErrorCode": error_code,
        "ErrorMessage": error_message,
        "Timestamp": datetime.utcnow().isoformat(),
        "ConnectionType": random.choice(connection_types),
        "ConnectionName": f"TestConnection_{random.randint(1,5)}",
        "AdditionalInfo": {
            "requestId": f"test_{random.randint(1000,9999)}",
            "component": "test-script"
        }
    }
    
    response = requests.post(url, json=payload)
    print(f"Sent error {error_code}: {response.status_code}")

# Send a few test errors
if __name__ == "__main__":
    print("Sending test errors...")
    while True:
        send_test_error()
        time.sleep(2)  # Wait 2 seconds between errors 