# import requests
# import json
# import time

# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# MOUSER_API_KEY = '109e0f93-5c4f-4b85-bf38-432ca0e46498'

# def search_mouser_part(part_number):
#     url = f"https://api.mouser.com/api/v1/search/partnumber?apiKey={MOUSER_API_KEY}"
#     headers = {'Content-Type': 'application/json'}

#     payload = {
#         'SearchByPartRequest': {
#             'mouserPartNumber': part_number,
#             'partSearchOptions': 'Exact'
#         }
#     }

#     try:
#         response = requests.post(url, headers=headers, json=payload, verify= False)
#         response.raise_for_status()
#         data = response.json()

#         print(f"\n🔎 Part: {part_number}")
#         print("=" * 80)
#         print(json.dumps(data, indent=2))
#         print("=" * 80)

#         return data
#     except requests.exceptions.RequestException as e:
#         print(f"❌ API request failed for {part_number}: {e}")
#         return None

# # === Part List ===
# parts_to_test = [
#     "BC847B",
#     "MBRS360",
#     "RD3L080SNFRA",
#     "DWW-KZKG_Typ"
# ]

# if __name__ == "__main__":
#     for part in parts_to_test:
#         search_mouser_part(part)
#         time.sleep(1.5)  # Wait to respect API rate limits

import requests
import json
import time


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


MOUSER_API_KEY = '109e0f93-5c4f-4b85-bf38-432ca0e46498'

def search_mouser_part(part_number):
    url = f"https://api.mouser.com/api/v1/search/partnumber?apiKey={MOUSER_API_KEY}"
    headers = {'Content-Type': 'application/json'}

    payload = {
        'SearchByPartRequest': {
            'mouserPartNumber': part_number,
            'partSearchOptions': 'Exact'
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload,verify=False)
        response.raise_for_status()
        data = response.json()

        # Extract product attributes
        results = data.get("SearchResults", {}).get("Parts", [])
        if not results:
            print(f"⚠️ No parts found for {part_number}")
            return

        attributes = results[0].get("ProductAttributes", [])
        
        print("=" * 60)
        for attr in attributes:
            print(f"{attr.get('AttributeName')}: {attr.get('AttributeValue')}")
        print("=" * 60)

        print(f"\n🔎 Absolute Maximum Ratings for {part_number}")
        print("=" * 60)


        max_keywords = ["maximum", "collector", "emitter", "junction", "dissipation", "voltage", "current", "temperature", "power"]
        for attr in attributes:
            name = attr.get("AttributeName", "").lower()
            if any(keyword in name for keyword in max_keywords):
                print(f"{attr.get('AttributeName')}: {attr.get('AttributeValue')}")

        print("=" * 60)

    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed for {part_number}: {e}")

if __name__ == "__main__":
    search_mouser_part("BC847B")
