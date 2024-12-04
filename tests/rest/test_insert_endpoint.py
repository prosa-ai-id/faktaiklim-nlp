import json
from datetime import datetime

import requests

# API endpoint configuration
BASE_URL = "http://localhost:8091"  # Change this to your actual API base URL
ENDPOINT = "article"


def test_insert_article():
    # Test data
    payload = {
        "id": 19206,
        "title": "Akun Instagram Mengatasnamakan Rumah Sakit Hermina",
        "created_by": "Dedy",
        "localtime": "2022-12-21 07:50:56",
        "publish_localtime": None,
        "user_publish_date": "2022-12-14 07:00:00",
        "stamped_image_url": [
            "/media/images/issue/17f79afc-8ddc-4111-b82f-bc0756492641.png"
        ],
        "classification": "HOAKS",
        "category": "Disasters and Accidents",
        "status_name": "submitted",
        "status_reason": "empty",
        "status_created_by": "Dedy",
        "status_localtime": "2022-12-21 07:50:56",
        "tags": ["gempa", "karangasem"],
        "verify_url": [],
        "distributions": [],
        "source_description": "https://www.youtube.com/shorts/2c_zICAym7U",
    }

    # Item ID to test with
    item_id = 19206

    try:
        # Make the PUT request
        response = requests.put(
            f"{BASE_URL}/{ENDPOINT}/{item_id}",
            json=payload,
            headers={
                "Content-Type": "application/json",
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
    test_insert_article()
