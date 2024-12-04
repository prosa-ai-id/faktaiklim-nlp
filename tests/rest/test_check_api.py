import json

import requests

# API endpoint configuration
BASE_URL = "http://localhost:8091"  # Change this to your actual API base URL
ENDPOINT = "check"


def check():
    payload = {
        "text": "TOPIK ARTIKEL:\nkebijakan dan pemerintahan\nkonservasi lingkungan\nTEKS BERITA:\nProvinsi Gorontalo masuk dalam Program Laut Sejahtera..."
    }

    try:
        response = requests.post(
            f"{BASE_URL}/{ENDPOINT}",
            json=payload,
            headers={
                "x-api-key": "ebce2698dadf0593c979a2798c84e49a0",
            },
        )

        # Print the response details
        print(f"Status Code: {response.status_code}")
        print("\nResponse Headers:")
        print(json.dumps(dict(response.headers), indent=2))
        print("\nResponse Body:")
        print(
            json.dumps(response.json(), indent=2)
            if response.text
            else "No response body"
        )

        # Check if the request was successful
        if response.status_code == 200:
            print("\nTest Successful! ✅")
        else:
            print(f"\nTest Failed! ❌ Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"\nError occurred: {e}")


if __name__ == "__main__":
    check()
